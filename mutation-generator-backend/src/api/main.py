from fastapi import FastAPI, Request, HTTPException
import sys
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from src.models.mutation import MutationType, MutationBase, MutationCreate, Mutation

# Add the project root to Python path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

# Now we can import with the correct paths
from clinvar_setup.db import DB
from backend.app.mondo import Mondo

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get absolute path to mondo.owl
mondo_path = root_dir / 'backend' / 'app' / 'data' / 'mondo.owl'

# Initialize Mondo
mondo = Mondo(path_to_mondo_owl=str(mondo_path))

@app.get("/")
async def root():
    return {"message": "Mutation Generator API"}

@app.get("/test-mondo/{condition_name}")
async def test_mondo(condition_name: str):
    matches = mondo.matches(condition_name, [])
    return {"matches": list(matches)}

@app.get("/test-mondo-name/{mondo_id}")
async def test_mondo_name(mondo_id: str):
    if mondo_id in mondo.mondo_xref_to_name:
        name = mondo.mondo_xref_to_name[mondo_id]
        return {"mondo_id": mondo_id, "name": name}
    return {"error": "ID not found"}

@app.get("/test-db")
async def test_db():
    db = DB()
    try:
        db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mutations'")
        table_exists = db.cursor.fetchone() is not None
        return {"mutation_table_exists": table_exists}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/variants/process")
async def process_variants(request: Request):
    print("Endpoint hit!") # Debug log
    try:
        data = await request.json()
        print("Received data:", data) # Debug log
        gene_name = data.get("geneName")
        
        if not gene_name:
            raise HTTPException(status_code=400, detail="Gene name is required")
            
        return {
            "status": "success",
            "message": f"Received request for gene: {gene_name}",
            "gene": gene_name
        }
            
    except Exception as e:
        print("Error:", str(e)) # Debug log
        raise HTTPException(status_code=500, detail=str(e))
            
        # Initialize DB connection
        db = DB()
        
        try:
            # Query mutations for the gene
            mutations = db.cursor.execute("""
                SELECT * FROM mutations 
                WHERE gene_name = ? 
                ORDER BY position
            """, (gene_name.lower(),)).fetchall()
            
            # Format the results
            results = {
                "gene_name": gene_name,
                "mutations": [],
                "summary": {
                    "total_variants": len(mutations),
                    "by_type": {},
                    "by_significance": {}
                }
            }
            
            # Process each mutation
            for mut in mutations:
                mutation_data = {
                    "position": mut["position"],
                    "reference": mut["reference"],
                    "alternate": mut["alternate"],
                    "mutation_type": mut["mutation_type"],
                    "clinical_significance": mut["clinical_significance"],
                    "description": mut["description"]
                }
                results["mutations"].append(mutation_data)
                
                # Update summary statistics
                mut_type = mut["mutation_type"]
                results["summary"]["by_ty
        if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001)  # Make sure this is 8001