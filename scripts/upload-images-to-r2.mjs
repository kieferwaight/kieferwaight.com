import { createReadStream } from 'node:fs';
import { readdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { HeadObjectCommand, PutObjectCommand, S3Client } from '@aws-sdk/client-s3';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SOURCE_DIRECTORY = path.join(ROOT, 'public/assets/img');
const ACCOUNT_ID = process.env.CLOUDFLARE_ACCOUNT_ID ?? '5f920424d9df83f01ea9c30e43c99965';
const ENDPOINT = process.env.R2_ENDPOINT ?? `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`;
const PUBLIC_ORIGIN = 'https://images.kieferwaight.com';
const DRY_RUN = process.argv.includes('--dry-run');

const contentTypes = new Map([
    ['.afdesign', 'application/octet-stream'],
    ['.jpg', 'image/jpeg'],
    ['.png', 'image/png'],
    ['.svg', 'image/svg+xml'],
]);

function isLocalIcon(filePath) {
    const name = path.basename(filePath);
    return name.startsWith('favicon') || name === 'apple-touch-icon.png' || name.startsWith('android-chrome-');
}

async function collectFiles(directory) {
    const entries = await readdir(directory, { withFileTypes: true });
    const files = [];

    for (const entry of entries) {
        const filePath = path.join(directory, entry.name);
        if (entry.isDirectory()) {
            files.push(...await collectFiles(filePath));
        } else if (entry.isFile() && !isLocalIcon(filePath)) {
            files.push(filePath);
        }
    }

    return files.sort();
}

function objectKey(filePath) {
    return path.relative(SOURCE_DIRECTORY, filePath).split(path.sep).join('/');
}

async function main() {
    const files = await collectFiles(SOURCE_DIRECTORY);
    const totalBytes = (await Promise.all(files.map((filePath) => stat(filePath)))).reduce(
        (total, file) => total + file.size,
        0,
    );

    if (DRY_RUN) {
        console.log(`Would upload ${files.length} assets (${(totalBytes / 1024 / 1024).toFixed(1)} MiB) to ${PUBLIC_ORIGIN}.`);
        for (const filePath of files) console.log(objectKey(filePath));
        return;
    }

    const bucket = process.env.R2_BUCKET;
    if (!bucket) throw new Error('R2_BUCKET must be set.');
    if (!process.env.AWS_ACCESS_KEY_ID || !process.env.AWS_SECRET_ACCESS_KEY) {
        throw new Error('AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set.');
    }
    if (process.env.AWS_ACCESS_KEY_ID.length !== 32) {
        throw new Error('AWS_ACCESS_KEY_ID must be the 32-character R2 Access Key ID.');
    }
    if (process.env.AWS_SECRET_ACCESS_KEY.length !== 64) {
        throw new Error('AWS_SECRET_ACCESS_KEY must be the 64-character R2 Secret Access Key.');
    }

    const client = new S3Client({
        region: 'auto',
        endpoint: ENDPOINT,
        credentials: {
            accessKeyId: process.env.AWS_ACCESS_KEY_ID,
            secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
        },
    });

    for (const filePath of files) {
        const key = objectKey(filePath);
        const contentType = contentTypes.get(path.extname(filePath).toLowerCase()) ?? 'application/octet-stream';
        await client.send(new PutObjectCommand({
            Bucket: bucket,
            Key: key,
            Body: createReadStream(filePath),
            ContentType: contentType,
            CacheControl: 'public, max-age=31536000, immutable',
        }));
        await client.send(new HeadObjectCommand({ Bucket: bucket, Key: key }));

        const response = await fetch(`${PUBLIC_ORIGIN}/${key}`, { method: 'HEAD' });
        if (!response.ok) throw new Error(`${key} uploaded but ${PUBLIC_ORIGIN} returned ${response.status}.`);
        console.log(`Uploaded and verified ${key}`);
    }
}

main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
});