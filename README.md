# Backend Test Submission

## Overview

Flask-based URL shortener using in-memory storage (no database).

## Features

- Create short URLs with optional custom shortcode and expiry
- Redirect to original URL
- View usage stats: click count and detailed logs

## API Endpoints

### 1. Create Short URL
- **POST** `/shorturls`
```json
{
  "url": "https://google.com",
  "validity": 30,
  "shortcode": "g123"
}