import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Path to the carbon data JSON file
    const filePath = path.join(process.cwd(), '..', 'backend', 'app', 'models', 'carbon_data.json');
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return NextResponse.json(
        { error: 'Carbon data file not found' },
        { status: 404 }
      );
    }
    
    // Read the file
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const carbonData = JSON.parse(fileContent);
    
    return NextResponse.json(carbonData);
  } catch (error) {
    console.error('Error reading carbon data:', error);
    return NextResponse.json(
      { error: 'Failed to read carbon data' },
      { status: 500 }
    );
  }
}
