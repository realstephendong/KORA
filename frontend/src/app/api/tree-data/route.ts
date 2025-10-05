import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Path to the tree data JSON file
    const filePath = path.join(process.cwd(), '..', 'backend', 'app', 'models', 'tree_data.json');
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return NextResponse.json(
        { error: 'Tree data file not found' },
        { status: 404 }
      );
    }
    
    // Read the file
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const treeData = JSON.parse(fileContent);
    
    return NextResponse.json(treeData);
  } catch (error) {
    console.error('Error reading tree data:', error);
    return NextResponse.json(
      { error: 'Failed to read tree data' },
      { status: 500 }
    );
  }
}
