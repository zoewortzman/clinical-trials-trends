import { supabase } from '../../lib/supabaseClient'
import { NextResponse } from "next/server";

export async function GET(): Promise<NextResponse> {
  try {
    const { data: elderlyData, count: elderlyCount, error: elderlyError } = await supabase
      .from('clinical_trials')
      .select('age', { count: 'exact' })
      .or('age.ilike.%elderly%,age.ilike.%older_adult%'); 
    
    const { count: totalCount, error: totalError } = await supabase
      .from('clinical_trials')
      .select('*', { count: 'exact', head: true });
    
    if (elderlyError) throw new Error(elderlyError.message);
    if (totalError) throw new Error(totalError.message);

    return NextResponse.json({
      elderlyCount,
      totalCount,
    });
  } catch (error) {
    return NextResponse.json({ error }, { status: 500 });
  }
}
