import { supabase } from '../../lib/supabaseClient'
import { NextResponse } from "next/server";

export async function GET(): Promise<NextResponse> {
  try {
    // count number of rows from each source
    const { count: euCount, error: euError } = await supabase
      .from('combined_trials')
      .select('source', { count: 'exact' })
      .eq('source', 'EudraCT');

    const { count: usCount, error: usError } = await supabase
    .from('combined_trials')
    .select('source', { count: 'exact' })
    .eq('source', 'ClinicalTrials.gov');

    
    if (euError) throw new Error(euError.message);
    if (usError) throw new Error(usError.message);

    return NextResponse.json({
      euCount,
      usCount,
    });
  } catch (error) {
    return NextResponse.json({ error }, { status: 500 });
  }
}
