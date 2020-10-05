FROM gitpod/workspace-postgres
                    
USER gitpod

# gitpod DEV enviroment variables:
ENV PATH="$PATH:/usr/lib/postgresql/12/bin"
ENV DATABASE_URL=postgresql://localhost:5432/postgres?user=gitpod 