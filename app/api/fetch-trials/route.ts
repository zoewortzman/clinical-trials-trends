import { supabase } from '../../lib/supabaseClient'
import { NextResponse } from "next/server";

export async function GET(): Promise<NextResponse> {
  try {
    // pull all data from supabases
    const { data, error } = await supabase
    .from('combined_trials').select('*');
    if (error) {
      throw new Error(error.message);
    }
    // Return the data in the response as JSON
    return NextResponse.json({ data });
  } catch (error ) {
    // If an error occurs, catch it and return a JSON response with the error message
    return NextResponse.json({ error }, { status: 500 });
  }
}
