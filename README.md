# Real Estate API

A RESTful API for managing real estate listings, users, and transactions. This API allows you to manage real estate listings (advertisements), user accounts, and transactions in the real estate domain.

## Features

- **User Management**: User registration, authentication, and profile management
- **Real Estate Listings**: Create, update, and manage property advertisements
- **Category Management**: Hierarchical category system with icon support
- **File Uploads**: S3 integration for image and file storage
- **Search & Filtering**: Advanced search capabilities for properties

## Category Icons

Categories now support custom icons that are stored in AWS S3:

- **Upload Icon**: `POST /api/v1/categories/{category_id}/icon`
- **Delete Icon**: `DELETE /api/v1/categories/{category_id}/icon`
- **Supported Formats**: JPEG, PNG, GIF, WebP
- **Max File Size**: 5MB
- **Storage**: AWS S3 with public read access

## Environment Variables

Make sure to set the following environment variables for S3 functionality:

```bash
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
```
