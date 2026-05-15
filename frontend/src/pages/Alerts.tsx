import { useState, useEffect, useContext } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { RoleContext } from '@/contexts/RoleContext';
import { AlertCircle, CheckCircle2, XCircle, Clock } from 'lucide-react';

interface Alert {
  id: string;
  type: 'activity' | 'inactivity' | 'pattern_change' | 'missing_routine';
  severity: 'low' | 'medium' | 'high';
  summary: string;
  explanation: string;
  timestamp: string;
  status: 'active' | 'resolved' | 'dismissed';
  confidence: number;
  actions?: string[];
}

export default function AlertsPage() {
  const { role } = useContext(RoleContext);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState<'all' | 'active' | 'resolved'>('active');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, [role]);

  const fetchAlerts = async () => {
    try {
      const response = await fetch(`/alerts?role=${role}`);
      const data = await response.json();
      setAlerts(data);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (alertId: string, action: 'approve' | 'reject') => {
    try {
      await fetch('/alerts/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alert_id: alertId, action }),
      });
      fetchAlerts();
    } catch (error) {
      console.error('Failed to handle alert action:', error);
    }
  };

  const filteredAlerts = alerts.filter((alert) => {
    if (filter === 'all') return true;
    return alert.status === (filter === 'active' ? 'active' : 'resolved');
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'resolved':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      default:
        return <XCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  if (loading) {
    return <div className="p-6 text-center">Loading alerts...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Alerts</h1>
        <p className="text-gray-600 mt-2">Monitor and manage care alerts</p>
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-2">
        {(['all', 'active', 'resolved'] as const).map((f) => (
          <Button
            key={f}
            variant={filter === f ? 'default' : 'outline'}
            onClick={() => setFilter(f)}
            className="capitalize"
          >
            {f}
          </Button>
        ))}
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center text-gray-500">
              No {filter} alerts found
            </CardContent>
          </Card>
        ) : (
          filteredAlerts.map((alert) => (
            <Card key={alert.id} className="border-l-4 border-l-red-500">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    {getStatusIcon(alert.status)}
                    <div className="flex-1">
                      <CardTitle className="text-lg">{alert.summary}</CardTitle>
                      <CardDescription className="mt-1">{alert.explanation}</CardDescription>
                    </div>
                  </div>
                  <Badge className={getSeverityColor(alert.severity)}>
                    {alert.severity}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="w-4 h-4" />
                  {new Date(alert.timestamp).toLocaleString()}
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span>Confidence: {Math.round(alert.confidence * 100)}%</span>
                  <span className="text-gray-500">Type: {alert.type.replace(/_/g, ' ')}</span>
                </div>

                {/* Action Buttons */}
                {alert.status === 'active' && role === 'caregiver' && (
                  <div className="flex gap-2 pt-2">
                    <Button
                      size="sm"
                      onClick={() => handleAction(alert.id, 'approve')}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      Acknowledge
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleAction(alert.id, 'reject')}
                    >
                      Dismiss
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Summary Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Alert Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <div className="text-2xl font-bold">
                {alerts.filter((a) => a.status === 'active').length}
              </div>
              <div className="text-sm text-gray-600">Active</div>
            </div>
            <div>
              <div className="text-2xl font-bold">
                {alerts.filter((a) => a.severity === 'high').length}
              </div>
              <div className="text-sm text-gray-600">High Priority</div>
            </div>
            <div>
              <div className="text-2xl font-bold">{alerts.length}</div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
