# Deployment Guide

## Prerequisites
- Docker and Docker Compose
- Python 3.10+
- Node.js 18+
- PostgreSQL (or Supabase cloud)
- Qdrant Cloud account
- Redis (cloud or local)

## Local Development

```bash
# Clone and setup
git clone <repo>
cd rag-system

# Copy environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Start services
docker-compose up
```

## Production Deployment

### Using Docker Swarm
```bash
docker swarm init
docker stack deploy -c docker-compose.yml rag-system
```

### Using Kubernetes
```bash
kubectl apply -f k8s/
```

### Environment Variables
All critical configuration comes from `.env`:
- `HUGGINGFACE_API_KEY` - For embeddings
- `QDRANT_URL` - Vector database
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Cache store
- `WANDB_API_KEY` - Monitoring

## Scaling Considerations

1. **Vector Store**: Use Qdrant Cloud for scalability
2. **Database**: Use managed PostgreSQL (Supabase, AWS RDS)
3. **Cache**: Redis Cluster for high traffic
4. **Backend**: Deploy multiple FastAPI instances with load balancer
5. **Frontend**: Deploy to CDN (Vercel, Netlify)

## Monitoring
- Application metrics: Weights & Biases integration
- Infrastructure: CloudWatch/Datadog
- Custom dashboards for RAG-specific metrics
