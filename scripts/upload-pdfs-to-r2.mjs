import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { readdir, readFile } from 'node:fs/promises';
import { HeadObjectCommand, PutObjectCommand, S3Client } from '@aws-sdk/client-s3';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const pdfDir = path.join(root, 'dist', 'pdfs');

const ACCOUNT_ID = process.env.CLOUDFLARE_ACCOUNT_ID ?? '5f920424d9df83f01ea9c30e43c99965';
const ENDPOINT = process.env.R2_ENDPOINT ?? `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`;
const PUBLIC_ORIGIN = 'https://images.kieferwaight.com';
const KEY_PREFIX = 'pdfs';
const DRY_RUN = process.argv.includes('--dry-run');

async function listLocalPdfs() {
    const entries = await readdir(pdfDir, { withFileTypes: true }).catch(() => []);
    return entries.filter((entry) => entry.isFile() && entry.name.endsWith('.pdf')).map((entry) => entry.name).sort();
}

async function verifyPublicUrl(key) {
    const response = await fetch(`${PUBLIC_ORIGIN}/${key}`, { method: 'HEAD' });
    if (!response.ok) throw new Error(`${key} uploaded but ${PUBLIC_ORIGIN} returned ${response.status}.`);
}

async function uploadPdf(client, bucket, fileName) {
    const key = `${KEY_PREFIX}/${fileName}`;
    const body = await readFile(path.join(pdfDir, fileName));
    await client.send(new PutObjectCommand({
        Bucket: bucket,
        Key: key,
        Body: body,
        ContentType: 'application/pdf',
        CacheControl: 'public, max-age=3600',
    }));
    await client.send(new HeadObjectCommand({ Bucket: bucket, Key: key }));
    await verifyPublicUrl(key);
    console.log(`Uploaded and verified ${key}`);
}

async function main() {
    const fileNames = await listLocalPdfs();
    if (fileNames.length === 0) {
        console.log('pdfs:upload: no PDFs found in dist/pdfs, run `npm run build` first.');
        return;
    }

    if (DRY_RUN) {
        console.log(`Would upload ${fileNames.length} PDFs to R2 under ${KEY_PREFIX}/.`);
        for (const fileName of fileNames) console.log(fileName);
        return;
    }

    const bucket = process.env.R2_BUCKET;
    if (!bucket) throw new Error('R2_BUCKET must be set.');
    if (!process.env.AWS_ACCESS_KEY_ID || !process.env.AWS_SECRET_ACCESS_KEY) {
        throw new Error('AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set.');
    }

    const client = new S3Client({
        region: 'auto',
        endpoint: ENDPOINT,
        credentials: {
            accessKeyId: process.env.AWS_ACCESS_KEY_ID,
            secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
        },
    });

    for (const fileName of fileNames) await uploadPdf(client, bucket, fileName);
}

main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
});
