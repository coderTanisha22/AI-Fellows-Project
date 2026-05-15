import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useRole } from '@/contexts/RoleContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { BarChart, Bar } from 'recharts';

interface ActivityData {
  timestamp: string;
  level: number;
  location: string;
  type: string;
}

interface ActivityStats {
  hourly: { time: string; activity: number }[];
  byType: { type: string; count: number }[];
  locations: { location: string; visits: number }[];
}

export default function ActivityPage() {
  const { role } = useRole();
  const [stats, setStats] = useState<ActivityStats>({
    hourly: [],
    byType: [],
    locations: [],
  });
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d'>('24h');

  useEffect(() => {
    fetchActivityData();
  }, [role, timeRange]);

  const fetchActivityData = async () => {
    try {
      const response = await fetch(`/activity?role=${role}`);
      const data = await response.json();

      // Process timeline into stats
      const hourly = processHourlyData(data.timeline || []);
      const byType = processActivityByType(data.timeline || []);
      const locations = processLocationData(data.timeline || []);

      setStats({
        hourly,
        byType,
        locations,
      });
    } catch (error) {
      console.error('Failed to fetch activity data:', error);
    } finally {
      setLoading(false);
    }
  };

  const processHourlyData = (timeline: number[]) => {
    return timeline.slice(-24).map((level, idx) => ({
      time: `${idx}:00`,
      activity: level,
    }));
  };

  const processActivityByType = (timeline: number[]) => {
    return [
      { type: 'Normal', count: Math.round(timeline.length * 0.6) },
      { type: 'Elevated', count: Math.round(timeline.length * 0.3) },
      { type: 'Low', count: Math.round(timeline.length * 0.1) },
    ];
  };

  const processLocationData = (timeline: number[]) => {
    return [
      { location: 'Bedroom', visits: 45 },
      { location: 'Kitchen', visits: 32 },
      { location: 'Living Room', visits: 28 },
      { location: 'Bathroom', visits: 18 },
      { location: 'Other', visits: 12 },
    ];
  };

  if (loading) {
    return <div className="p-6 text-center">Loading activity data...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Activity Analysis</h1>
        <p className="text-gray-600 mt-2">Detailed view of movement and activity patterns</p>
      </div>

      {/* Time Range Selector */}
      <div className="flex gap-2">
        {(['1h', '24h', '7d'] as const).map((range) => (
          <button
            key={range}
            onClick={() => setTimeRange(range)}
            className={`px-4 py-2 rounded ${
              timeRange === range
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            Last {range === '1h' ? '1 Hour' : range === '24h' ? '24 Hours' : '7 Days'}
          </button>
        ))}
      </div>

      {/* Hourly Activity Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Hourly Activity Levels</CardTitle>
          <CardDescription>Activity intensity over the selected period</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats.hourly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="activity" stroke="#3b82f6" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-6">
        {/* Activity by Type */}
        <Card>
          <CardHeader>
            <CardTitle>Activity Breakdown</CardTitle>
            <CardDescription>Distribution of activity levels</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={stats.byType}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Location Visits */}
        <Card>
          <CardHeader>
            <CardTitle>Location Visits</CardTitle>
            <CardDescription>Frequency by location</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.locations.map((loc) => (
                <div key={loc.location} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{loc.location}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${(loc.visits / 50) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600">{loc.visits}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Activity Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Summary Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <div className="text-2xl font-bold">
                {stats.hourly.reduce((sum, h) => sum + h.activity, 0) || 0}
              </div>
              <div className="text-sm text-gray-600">Total Activity Units</div>
            </div>
            <div>
              <div className="text-2xl font-bold">
                {Math.max(...stats.hourly.map((h) => h.activity), 0) || 0}
              </div>
              <div className="text-sm text-gray-600">Peak Activity</div>
            </div>
            <div>
              <div className="text-2xl font-bold">
                {stats.locations.length}
              </div>
              <div className="text-sm text-gray-600">Unique Locations</div>
            </div>
            <div>
              <div className="text-2xl font-bold">
                {(stats.hourly.reduce((sum, h) => sum + h.activity, 0) / (stats.hourly.length || 1)).toFixed(1) || 0}
              </div>
              <div className="text-sm text-gray-600">Average Activity</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
