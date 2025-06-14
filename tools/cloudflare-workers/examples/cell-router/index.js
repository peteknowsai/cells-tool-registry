// Example Cloudflare Worker with Durable Object

export class CellRegistry {
  constructor(ctx, env) {
    this.state = ctx.state;
    this.env = env;
  }

  async fetch(request) {
    const url = new URL(request.url);
    
    switch (url.pathname) {
      case '/register':
        return this.handleRegister(request);
      case '/list':
        return this.handleList();
      case '/get':
        return this.handleGet(url);
      default:
        return new Response('Not found', { status: 404 });
    }
  }

  async handleRegister(request) {
    const data = await request.json();
    const cellId = data.cellId;
    const metadata = data.metadata || {};
    
    await this.state.storage.put(`cell:${cellId}`, {
      ...metadata,
      registeredAt: new Date().toISOString()
    });
    
    return Response.json({
      success: true,
      cellId,
      message: 'Cell registered successfully'
    });
  }

  async handleList() {
    const cells = [];
    const entries = await this.state.storage.list({ prefix: 'cell:' });
    
    for (const [key, value] of entries) {
      cells.push({
        cellId: key.replace('cell:', ''),
        ...value
      });
    }
    
    return Response.json({ cells });
  }

  async handleGet(url) {
    const cellId = url.searchParams.get('cellId');
    if (!cellId) {
      return Response.json({ error: 'cellId required' }, { status: 400 });
    }
    
    const cell = await this.state.storage.get(`cell:${cellId}`);
    if (!cell) {
      return Response.json({ error: 'Cell not found' }, { status: 404 });
    }
    
    return Response.json({ cellId, ...cell });
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // Route to appropriate cell based on subdomain
    const hostname = url.hostname;
    const cellMatch = hostname.match(/^([^.]+)\.cells\./);
    
    if (cellMatch) {
      const cellId = cellMatch[1];
      
      // Get or create durable object for this cell
      const id = env.CELL_REGISTRY.idFromName(cellId);
      const stub = env.CELL_REGISTRY.get(id);
      
      // Forward request to durable object
      return stub.fetch(request);
    }
    
    // Default response for non-cell requests
    return new Response(JSON.stringify({
      message: 'Cell Router',
      usage: 'Access cells via {cellId}.cells.yourdomain.com',
      endpoints: [
        'POST /register - Register a new cell',
        'GET /list - List all cells',
        'GET /get?cellId=xxx - Get specific cell'
      ]
    }, null, 2), {
      headers: { 'Content-Type': 'application/json' }
    });
  }
}