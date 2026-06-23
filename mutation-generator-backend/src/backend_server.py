from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

# Initialize FastAPI app
app = FastAPI(title="Mutation Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection helper
def get_db():
    conn = sqlite3.connect('clinvar.db')
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models
class Submission(BaseModel):
    date: str
    variant_name: str
    variant_frequency: Optional[float]
    gene: Optional[str]
    submitter_name: str
    significance: str
    condition_name: str
    method: str

class VariantDetail(BaseModel):
    variant_name: str
    gene: str
    significance: str
    condition_name: str
    total_submissions: int
    conflicting_interpretations: bool

# API endpoints
@app.get("/variants/", response_model=List[VariantDetail])
async def get_variants(
    gene: Optional[str] = None,
    significance: Optional[str] = None,
    limit: int = 100
):
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            variant_name,
            gene,
            significance,
            condition_name,
            COUNT(DISTINCT scv) as total_submissions,
            COUNT(DISTINCT significance) > 1 as has_conflicts
        FROM submissions
        WHERE date = (SELECT MAX(date) FROM submissions)
    """
    
    conditions = []
    params = []
    
    if gene:
        conditions.append("gene = ?")
        params.append(gene)
        
    if significance:
        conditions.append("significance = ?")
        params.append(significance)
        
    if conditions:
        query += " AND " + " AND ".join(conditions)
        
    query += " GROUP BY variant_name LIMIT ?"
    params.append(limit)
    
    try:
        cursor.execute(query, params)
        variants = cursor.fetchall()
        return [
            VariantDetail(
                variant_name=v['variant_name'],
                gene=v['gene'] or 'Unknown',
                significance=v['significance'],
                condition_name=v['condition_name'],
                total_submissions=v['total_submissions'],
                conflicting_interpretations=bool(v['has_conflicts'])
            )
            for v in variants
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/variants/{variant_name}/submissions", response_model=List[Submission])
async def get_variant_submissions(variant_name: str):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                date,
                variant_name,
                variant_frequency,
                gene,
                submitter_name,
                significance,
                condition_name,
                method
            FROM submissions 
            WHERE variant_name = ?
            AND date = (SELECT MAX(date) FROM submissions)
        """, (variant_name,))
        
        submissions = cursor.fetchall()
        if not submissions:
            raise HTTPException(status_code=404, detail="Variant not found")
            
        return [
            Submission(
                date=s['date'],
                variant_name=s['variant_name'],
                variant_frequency=s['variant_frequency'],
                gene=s['gene'],
                submitter_name=s['submitter_name'],
                significance=s['significance'],
                condition_name=s['condition_name'],
                method=s['method']
            )
            for s in submissions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/genes")
async def get_genes():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT DISTINCT gene
            FROM submissions
            WHERE date = (SELECT MAX(date) FROM submissions)
            AND gene IS NOT NULL
            AND gene != ''
            ORDER BY gene
        """)
        
        genes = [row[0] for row in cursor.fetchall()]
        return genes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/conditions")
async def get_conditions():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT DISTINCT condition_name
            FROM submissions
            WHERE date = (SELECT MAX(date) FROM submissions)
            ORDER BY condition_name
        """)
        
        conditions = [row[0] for row in cursor.fetchall()]
        return conditions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)