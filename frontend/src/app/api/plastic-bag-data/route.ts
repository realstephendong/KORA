import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Path to the plastic bag data JSON file
    const filePath = path.join(process.cwd(), '..', 'backend', 'app', 'models', 'plastic_bag_data.json');
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return NextResponse.json(
        { error: 'Plastic bag data file not found' },
        { status: 404 }
      );
    }
    
    // Read the file
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const plasticBagData = JSON.parse(fileContent);
    
    return NextResponse.json(plasticBagData);
  } catch (error) {
    console.error('Error reading plastic bag data:', error);
    return NextResponse.json(
      { error: 'Failed to read plastic bag data' },
      { status: 500 }
    );
  }
}
