import path from 'node:path';
import { readFile } from 'node:fs/promises';
import sharp from 'sharp';
import { HeadObjectCommand, PutObjectCommand, S3Client } from '@aws-sdk/client-s3';

const ACCOUNT_ID = process.env.CLOUDFLARE_ACCOUNT_ID ?? '5f920424d9df83f01ea9c30e43c99965';
const ENDPOINT = process.env.R2_ENDPOINT ?? `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`;
const PUBLIC_ORIGIN = 'https://images.kieferwaight.com';
const WIDTHS = [480, 768, 960, 1440];

const contentTypes = new Map([
    ['.jpg', 'image/jpeg'],
    ['.jpeg', 'image/jpeg'],
    ['.png', 'image/png'],
    ['.webp', 'image/webp'],
]);

function variantKey(key, width) {
    const extension = path.extname(key);
    return `${key.slice(0, -extension.length)}-w${width}.webp`;
}

async function verifyPublicUrl(key) {
    const response = await fetch(`${PUBLIC_ORIGIN}/${key}`, { method: 'HEAD' });
    if (!response.ok) throw new Error(`${key} uploaded but ${PUBLIC_ORIGIN} returned ${response.status}.`);
}

async function uploadObject(client, bucket, key, body, contentType) {
    await client.send(new PutObjectCommand({
        Bucket: bucket,
        Key: key,
        Body: body,
        ContentType: contentType,
        CacheControl: 'public, max-age=31536000, immutable',
    }));
    await client.send(new HeadObjectCommand({ Bucket: bucket, Key: key }));
    await verifyPublicUrl(key);
}

async function main() {
    const [localPath, destKey] = process.argv.slice(2);
    if (!localPath || !destKey) {
        console.error('Usage: node scripts/add-image.mjs <local-file-path> <r2-destination-key>');
        console.error('Example: node scripts/add-image.mjs ~/Desktop/photo.jpg archive/2026-photo.jpg');
        process.exitCode = 1;
        return;
    }

    const extension = path.extname(destKey).toLowerCase();
    const contentType = contentTypes.get(extension);
    if (!contentType) throw new Error(`Unsupported extension "${extension}". Use .jpg, .jpeg, .png, or .webp.`);

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

    const source = await readFile(localPath);
    await uploadObject(client, bucket, destKey, source, contentType);
    console.log(`Uploaded original: ${destKey}`);

    for (const width of WIDTHS) {
        const keyForVariant = variantKey(destKey, width);
        const body = await sharp(source).resize({ width }).webp({ quality: 80 }).toBuffer();
        await uploadObject(client, bucket, keyForVariant, body, contentTypes.get('.webp'));
        console.log(`Uploaded variant: ${keyForVariant}`);
    }

    console.log(`Done. Reference this image in content as: ${PUBLIC_ORIGIN}/${destKey}`);
}

main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
});
