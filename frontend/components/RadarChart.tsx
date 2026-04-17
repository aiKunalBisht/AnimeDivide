"use client";

import { ResponsiveContainer, RadarChart as RechartsRadarChart, PolarGrid, PolarAngleAxis, Radar, Tooltip, Legend } from "recharts";

export default function RadarChart({ data }: { data: any[] }) {
  return (
    <div className="w-full h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis dataKey="topic" tick={{ fill: '#9CA3AF', fontSize: 13, fontWeight: 600 }} />
          <Tooltip 
             contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '0.75rem', color: '#F3F4F6' }}
             itemStyle={{ fontWeight: 'bold' }}
          />
          <Legend wrapperStyle={{ paddingTop: '20px' }} />
          <Radar name="JP Score" dataKey="jp_score" stroke="#EF4444" strokeWidth={3} fill="#EF4444" fillOpacity={0.4} />
          <Radar name="EN Score" dataKey="en_score" stroke="#3B82F6" strokeWidth={3} fill="#3B82F6" fillOpacity={0.4} />
        </RechartsRadarChart>
      </ResponsiveContainer>
    </div>
  );
}
