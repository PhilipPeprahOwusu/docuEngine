import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://136.116.180.162';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'GET');
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'POST');
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'PUT');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'DELETE');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'PATCH');
}

async function proxyRequest(
  request: NextRequest,
  path: string[],
  method: string
) {
  try {
    // Reconstruct the full path including /api prefix
    const targetPath = path.join('/');
    const url = `${BACKEND_URL}/api/${targetPath}`;
    const searchParams = request.nextUrl.searchParams.toString();
    const targetUrl = searchParams ? `${url}?${searchParams}` : url;

    // Get request headers
    const headers: Record<string, string> = {};
    request.headers.forEach((value, key) => {
      // Skip host header to avoid conflicts
      if (key.toLowerCase() !== 'host') {
        headers[key] = value;
      }
    });

    // Get request body if present
    let body: any = undefined;
    const contentType = request.headers.get('content-type');

    if (method !== 'GET' && method !== 'HEAD') {
      if (contentType?.includes('application/json')) {
        try {
          body = await request.json();
          body = JSON.stringify(body);
        } catch {
          // Not JSON or empty body
        }
      } else if (contentType?.includes('application/x-www-form-urlencoded')) {
        body = await request.text();
      } else if (contentType?.includes('multipart/form-data')) {
        body = await request.formData();
      } else {
        try {
          body = await request.text();
        } catch {
          // Empty body
        }
      }
    }

    // Make request to backend
    const response = await fetch(targetUrl, {
      method,
      headers,
      body,
    });

    // Get response headers
    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      responseHeaders.set(key, value);
    });

    // Get response body
    const responseData = await response.arrayBuffer();

    return new NextResponse(responseData, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error: any) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Proxy request failed', details: error.message },
      { status: 500 }
    );
  }
}
