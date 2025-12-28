import { useState, useEffect } from 'react';
import { 
  MapPin, 
  Calendar, 
  Trophy, 
  Route, 
  Play, 
  Pause, 
  RotateCcw,
  BarChart3,
  Globe
} from 'lucide-react';
import { 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';

interface Stats {
  total_checkins: number;
  unique_venues: number;
  top_city: string;
  total_distance_km: number;
}

interface CheckinGeo {
  id: string;
  venue_name: string;
  lat: number;
  lng: number;
  timestamp: number;
  shout: string;
}

interface WeeklyData {
  week: string;
  count: number;
}

function App() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [timeline, setTimeline] = useState<WeeklyData[]>([]);
  const [geoData, setGeoData] = useState<CheckinGeo[]>([]);
  const [visiblePoints, setVisiblePoints] = useState<CheckinGeo[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackIndex, setPlaybackIndex] = useState(0);

  useEffect(() => {
    // Fetch initial data
    fetch('/api/stats').then(res => res.json()).then(setStats);
    fetch('/api/timeline/weekly').then(res => res.json()).then(setTimeline);
    fetch('/api/checkins/geo').then(res => res.json()).then(setGeoData);
  }, []);

  // Animation logic
  useEffect(() => {
    let interval: any;
    if (isPlaying && playbackIndex < geoData.length) {
      interval = setInterval(() => {
        setPlaybackIndex(prev => prev + 1);
      }, 100);
    } else {
      setIsPlaying(false);
    }
    return () => clearInterval(interval);
  }, [isPlaying, playbackIndex, geoData]);

  useEffect(() => {
    setVisiblePoints(geoData.slice(0, playbackIndex));
  }, [playbackIndex, geoData]);

  const resetPlayback = () => {
    setPlaybackIndex(0);
    setIsPlaying(false);
  };

  return (
    <div className="min-h-screen bg-gray-950 p-6 font-sans">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Swarm Insights
          </h1>
          <p className="text-gray-400">Your life, visualized through check-ins.</p>
        </div>
      </header>

      {/* Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <StatCard icon={<MapPin className="text-blue-400" />} label="Total Check-ins" value={stats?.total_checkins ?? '...'} />
        <StatCard icon={<Trophy className="text-yellow-400" />} label="Unique Venues" value={stats?.unique_venues ?? '...'} />
        <StatCard icon={<Globe className="text-green-400" />} label="Top City" value={stats?.top_city ?? '...'} />
        <StatCard icon={<Route className="text-purple-400" />} label="Total Distance" value={`${stats?.total_distance_km.toFixed(0) ?? '...'} km`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Chart */}
        <div className="lg:col-span-2 bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-6">
            <BarChart3 className="text-blue-400" />
            <h2 className="text-xl font-semibold">Activity Over Time</h2>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeline}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="week" stroke="#6b7280" fontSize={12} tickFormatter={(str) => str.split('-')[0]} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#f3f4f6' }}
                  itemStyle={{ color: '#60a5fa' }}
                />
                <Area type="monotone" dataKey="count" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCount)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Animation Controls */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Calendar className="text-purple-400" />
              <h2 className="text-xl font-semibold">Time Machine</h2>
            </div>
            <p className="text-gray-400 text-sm mb-6">
              Watch your journey unfold. From your first check-in to today.
            </p>
          </div>
          
          <div className="space-y-4">
             <div className="text-center">
                <span className="text-4xl font-mono text-blue-400">
                    {visiblePoints.length > 0 ? new Date(visiblePoints[visiblePoints.length - 1].timestamp * 1000).getFullYear() : '----'}
                </span>
                <p className="text-xs text-gray-500 uppercase tracking-widest mt-1">Current Progress</p>
             </div>
             
             <div className="flex justify-center gap-4">
                <button 
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="w-16 h-16 bg-blue-600 hover:bg-blue-500 rounded-full flex items-center justify-center transition-all active:scale-95 shadow-lg shadow-blue-900/20"
                >
                  {isPlaying ? <Pause /> : <Play className="ml-1" />}
                </button>
                <button 
                  onClick={resetPlayback}
                  className="w-16 h-16 bg-gray-800 hover:bg-gray-700 rounded-full flex items-center justify-center transition-all active:scale-95"
                >
                  <RotateCcw />
                </button>
             </div>
             
             <div className="w-full bg-gray-800 h-1 rounded-full overflow-hidden">
                <div 
                    className="bg-blue-500 h-full transition-all duration-300" 
                    style={{ width: `${(playbackIndex / geoData.length) * 100}%` }}
                />
             </div>
          </div>
        </div>

        {/* The Map */}
        <div className="lg:col-span-3 h-[500px] bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-2xl">
          <MapContainer center={[20, 0]} zoom={2} style={{ height: '100%', width: '100%' }}>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {visiblePoints.map((p, idx) => (
              <CircleMarker 
                key={p.id} 
                center={[p.lat, p.lng]} 
                radius={idx === visiblePoints.length - 1 ? 12 : 5}
                pathOptions={{ 
                    color: idx === visiblePoints.length - 1 ? '#60a5fa' : '#3b82f6',
                    fillColor: idx === visiblePoints.length - 1 ? '#60a5fa' : '#3b82f6',
                    fillOpacity: idx === visiblePoints.length - 1 ? 0.8 : 0.4,
                    weight: idx === visiblePoints.length - 1 ? 3 : 1
                }}
              >
                <Popup>
                  <div className="text-gray-900">
                    <p className="font-bold">{p.venue_name}</p>
                    <p className="text-xs text-gray-600">{new Date(p.timestamp * 1000).toLocaleDateString()}</p>
                    {p.shout && <p className="mt-1 italic">"{p.shout}"</p>}
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: any, label: string, value: any }) {
  return (
    <div className="bg-gray-900 border border-gray-800 p-6 rounded-2xl shadow-lg">
      <div className="flex items-center gap-3 mb-2">
        {icon}
        <span className="text-gray-400 text-sm font-medium">{label}</span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
}

export default App;
