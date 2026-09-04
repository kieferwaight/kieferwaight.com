import path from 'node:path';
import sharp from 'sharp';
import { GetObjectCommand, HeadObjectCommand, ListObjectsV2Command, PutObjectCommand, S3Client } from '@aws-sdk/client-s3';

const ACCOUNT_ID = process.env.CLOUDFLARE_ACCOUNT_ID ?? '5f920424d9df83f01ea9c30e43c99965';
const ENDPOINT = process.env.R2_ENDPOINT ?? `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`;
const PUBLIC_ORIGIN = 'https://images.kieferwaight.com';
const DRY_RUN = process.argv.includes('--dry-run');
const WIDTHS = [480, 768, 960, 1440];

const contentTypes = new Map([
    ['.jpg', 'image/jpeg'],
    ['.png', 'image/png'],
    ['.webp', 'image/webp'],
]);

function isSourceImage(key) {
    return /\.(?:jpe?g|png|webp)$/i.test(key) && !/-w\d+\.webp$/i.test(key);
}

function variantKey(key, width) {
    const extension = path.extname(key);
    return `${key.slice(0, -extension.length)}-w${width}.webp`;
}

async function listSourceImages(client, bucket) {
    const keys = [];
    let continuationToken;
    do {
        const result = await client.send(new ListObjectsV2Command({ Bucket: bucket, ContinuationToken: continuationToken }));
        keys.push(...(result.Contents ?? []).map(({ Key }) => Key).filter(isSourceImage));
        continuationToken = result.NextContinuationToken;
    } while (continuationToken);
    return keys.sort();
}

async function readObject(client, bucket, key) {
    const result = await client.send(new GetObjectCommand({ Bucket: bucket, Key: key }));
    return Buffer.from(await result.Body.transformToByteArray());
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

async function uploadVariants(client, bucket, key) {
    const source = await readObject(client, bucket, key);
    for (const width of WIDTHS) {
        const keyForVariant = variantKey(key, width);
        const body = await sharp(source).resize({ width }).webp({ quality: 80 }).toBuffer();
        await uploadObject(client, bucket, keyForVariant, body, contentTypes.get('.webp'));
        console.log(`Generated and verified ${keyForVariant}`);
    }
}

async function main() {
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

    const keys = await listSourceImages(client, bucket);
    if (DRY_RUN) {
        console.log(`Would generate responsive WebP variants for ${keys.length} R2 source images.`);
        for (const key of keys) console.log(key);
        return;
    }

    for (const key of keys) await uploadVariants(client, bucket, key);
}

main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
});