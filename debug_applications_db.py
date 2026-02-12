#!/usr/bin/env python3
"""
Debug script to check what applications exist in the database
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Load .env
env_path = os.path.join(os.getcwd(), "backend", ".env")
if os.path.exists(env_path):
    print(f"Loading environment from {env_path}")
    with open(env_path, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

# Fallbacks
if "MONGODB_URL" not in os.environ:
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017"

# Import settings after env load
try:
    from app.core.config import settings
    DB_NAME = settings.DATABASE_NAME
except ImportError:
    DB_NAME = "jwhd_ip_automation"

async def debug_applications():
    """Check what applications exist in the database"""
    
    print("🔍 Debugging Applications Database...")
    
    client = AsyncIOMotorClient(os.environ["MONGODB_URL"])
    db = client[DB_NAME]
    
    print(f"Connected to database: {DB_NAME}")
    
    # Check all collections
    collections = await db.list_collection_names()
    print(f"\n📋 Available collections: {collections}")
    
    # Check enhanced_applications collection
    if "enhanced_applications" in collections:
        print(f"\n🔍 Checking enhanced_applications collection...")
        count = await db.enhanced_applications.count_documents({})
        print(f"Total enhanced applications: {count}")
        
        if count > 0:
            print("\n📄 Sample applications:")
            async for app in db.enhanced_applications.find({}).limit(3):
                print(f"  - ID: {app.get('_id')}")
                print(f"    Title: {app.get('title', 'No title')}")
                print(f"    Application Number: {app.get('application_number', 'No number')}")
                print(f"    Created By: {app.get('created_by', 'No user')}")
                print(f"    Created At: {app.get('created_at', 'No date')}")
                print(f"    Workflow Status: {app.get('workflow_status', 'No status')}")
                print()
    else:
        print("❌ enhanced_applications collection does not exist")
    
    # Check patent_applications collection
    if "patent_applications" in collections:
        print(f"\n🔍 Checking patent_applications collection...")
        count = await db.patent_applications.count_documents({})
        print(f"Total patent applications: {count}")
        
        if count > 0:
            print("\n📄 Sample patent applications:")
            async for app in db.patent_applications.find({}).limit(3):
                print(f"  - ID: {app.get('_id')}")
                print(f"    Title: {app.get('title', 'No title')}")
                print(f"    Application Number: {app.get('application_number', 'No number')}")
                print(f"    Created By: {app.get('created_by', 'No user')}")
                print(f"    Created At: {app.get('created_at', 'No date')}")
                print(f"    Status: {app.get('status', 'No status')}")
                print(f"    Has Inventors: {len(app.get('inventors', []))}")
                print(f"    Has Applicants: {len(app.get('applicants', []))}")
                print()
    else:
        print("❌ patent_applications collection does not exist")
    
    # Check regular applications collection
    if "applications" in collections:
        print(f"\n🔍 Checking applications collection...")
        count = await db.applications.count_documents({})
        print(f"Total regular applications: {count}")
        
        if count > 0:
            print("\n📄 Sample applications:")
            async for app in db.applications.find({}).limit(3):
                print(f"  - ID: {app.get('_id')}")
                print(f"    Title: {app.get('title', 'No title')}")
                print(f"    Created By: {app.get('created_by', 'No user')}")
                print(f"    Created At: {app.get('created_at', 'No date')}")
                print()
    else:
        print("❌ applications collection does not exist")
    
    # Check processing_jobs collection
    if "processing_jobs" in collections:
        print(f"\n🔍 Checking processing_jobs collection...")
        count = await db.processing_jobs.count_documents({})
        print(f"Total processing jobs: {count}")
        
        if count > 0:
            print("\n📄 Recent processing jobs:")
            async for job in db.processing_jobs.find({}).sort("created_at", -1).limit(5):
                print(f"  - ID: {job.get('_id')}")
                print(f"    Status: {job.get('status', 'No status')}")
                print(f"    Job Type: {job.get('job_type', 'No type')}")
                print(f"    Created At: {job.get('created_at', 'No date')}")
                print(f"    User ID: {job.get('user_id', 'No user')}")
                print(f"    Result: {job.get('result', {}).get('status', 'No result')}")
                print()
    
    # Check documents collection
    if "documents" in collections:
        print(f"\n🔍 Checking documents collection...")
        count = await db.documents.count_documents({})
        print(f"Total documents: {count}")
        
        if count > 0:
            print("\n📄 Recent documents:")
            async for doc in db.documents.find({}).sort("created_at", -1).limit(3):
                print(f"  - ID: {doc.get('_id')}")
                print(f"    Filename: {doc.get('filename', 'No filename')}")
                print(f"    Status: {doc.get('status', 'No status')}")
                print(f"    Created At: {doc.get('created_at', 'No date')}")
                print(f"    User ID: {doc.get('user_id', 'No user')}")
                print()
    
    # Check users to see what user IDs exist
    if "users" in collections:
        print(f"\n👥 Checking users...")
        count = await db.users.count_documents({})
        print(f"Total users: {count}")
        
        if count > 0:
            print("\n👤 Users:")
            async for user in db.users.find({}):
                print(f"  - ID: {user.get('_id')}")
                print(f"    Email: {user.get('email', 'No email')}")
                print(f"    Name: {user.get('full_name', 'No name')}")
                print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_applications())