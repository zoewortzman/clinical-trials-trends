import { supabase } from '../../lib/supabaseClient'
import { NextResponse } from "next/server";

export async function GET(): Promise<NextResponse> {
  try {
    // count number of rows where the column age contains either "elderly" or "older_adult"
    const { data: elderlyData, count: elderlyCount, error: elderlyError } = await supabase
      .from('clinical_trials')
      .select('age', { count: 'exact' })
      .or('age.ilike.%elderly%,age.ilike.%older_adult%'); 
    // count total number of observations
    const { count: totalCount, error: totalError } = await supabase
      .from('clinical_trials')
      .select('*', { count: 'exact', head: true });
    
    if (elderlyError) throw new Error(elderlyError.message);
    if (totalError) throw new Error(totalError.message);

    // return number of rows that contains studies for elderly populations and total number of rows
    return NextResponse.json({
      elderlyCount,
      totalCount,
    });
  } catch (error) {
    return NextResponse.json({ error }, { status: 500 });
  }
}
