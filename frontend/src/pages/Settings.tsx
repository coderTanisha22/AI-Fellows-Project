import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useRole } from '@/contexts/RoleContext';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

interface Settings {
  alertThreshold: number;
  notificationsEnabled: boolean;
  autoApprove: boolean;
  anomalyTypes: {
    inactivity: boolean;
    patternChange: boolean;
    erraticBehavior: boolean;
    missingRoutine: boolean;
  };
  contactEmail: string;
  contactPhone: string;
}

export default function SettingsPage() {
  const { role, userName } = useRole();
  const [settings, setSettings] = useState<Settings>({
    alertThreshold: 0.7,
    notificationsEnabled: true,
    autoApprove: false,
    anomalyTypes: {
      inactivity: true,
      patternChange: true,
      erraticBehavior: true,
      missingRoutine: true,
    },
    contactEmail: 'contact@example.com',
    contactPhone: '+1-555-000-0000',
  });
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleAnomalyChange = (type: keyof Settings['anomalyTypes']) => {
    setSettings({
      ...settings,
      anomalyTypes: {
        ...settings.anomalyTypes,
        [type]: !settings.anomalyTypes[type],
      },
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your care monitoring preferences</p>
      </div>

      {/* Save Notification */}
      {saved && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-2 text-green-800">
          <CheckCircle2 className="w-5 h-5" />
          Settings saved successfully
        </div>
      )}

      {/* Account Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
          <CardDescription>Your profile and role</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Name</Label>
            <Input value={userName} disabled className="mt-1" />
          </div>
          <div>
            <Label>Role</Label>
            <Input value={role.charAt(0).toUpperCase() + role.slice(1)} disabled className="mt-1" />
          </div>
          <div>
            <Label>Account Type</Label>
            <Input
              value={role === 'family' ? 'Family Member' : role === 'supervisor' ? 'Supervisor' : 'Primary Caregiver'}
              disabled
              className="mt-1"
            />
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>How you receive alerts</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base">Enable Notifications</Label>
              <p className="text-sm text-gray-600">Receive alerts via email and push</p>
            </div>
            <Switch
              checked={settings.notificationsEnabled}
              onCheckedChange={(checked) =>
                setSettings({ ...settings, notificationsEnabled: checked })
              }
            />
          </div>

          {settings.notificationsEnabled && (
            <>
              <div>
                <Label>Contact Email</Label>
                <Input
                  type="email"
                  value={settings.contactEmail}
                  onChange={(e) => setSettings({ ...settings, contactEmail: e.target.value })}
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Contact Phone</Label>
                <Input
                  type="tel"
                  value={settings.contactPhone}
                  onChange={(e) => setSettings({ ...settings, contactPhone: e.target.value })}
                  className="mt-1"
                />
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Alert Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Alert Detection</CardTitle>
          <CardDescription>Configure which anomalies trigger alerts</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base">Inactivity Alerts</Label>
                <p className="text-sm text-gray-600">Alert when activity drops below threshold</p>
              </div>
              <Switch
                checked={settings.anomalyTypes.inactivity}
                onCheckedChange={() => handleAnomalyChange('inactivity')}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base">Pattern Change Alerts</Label>
                <p className="text-sm text-gray-600">Alert when behavior patterns change significantly</p>
              </div>
              <Switch
                checked={settings.anomalyTypes.patternChange}
                onCheckedChange={() => handleAnomalyChange('patternChange')}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base">Erratic Behavior Alerts</Label>
                <p className="text-sm text-gray-600">Alert when activity becomes unpredictable</p>
              </div>
              <Switch
                checked={settings.anomalyTypes.erraticBehavior}
                onCheckedChange={() => handleAnomalyChange('erraticBehavior')}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base">Missing Routine Alerts</Label>
                <p className="text-sm text-gray-600">Alert when expected activities don't occur</p>
              </div>
              <Switch
                checked={settings.anomalyTypes.missingRoutine}
                onCheckedChange={() => handleAnomalyChange('missingRoutine')}
              />
            </div>
          </div>

          <div>
            <Label>Alert Threshold</Label>
            <p className="text-sm text-gray-600 mb-2">
              Confidence level required to trigger alerts ({Math.round(settings.alertThreshold * 100)}%)
            </p>
            <input
              type="range"
              min="0.5"
              max="0.99"
              step="0.05"
              value={settings.alertThreshold}
              onChange={(e) => setSettings({ ...settings, alertThreshold: parseFloat(e.target.value) })}
              className="w-full"
            />
          </div>
        </CardContent>
      </Card>

      {/* Privacy Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Privacy & Security</CardTitle>
          <CardDescription>Manage your data preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-2 text-blue-800 text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <strong>Note:</strong> All data is encrypted in transit. Activity data is retained for 30 days for
              analysis purposes.
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base">Data Sharing</Label>
              <p className="text-sm text-gray-600">Allow other caregivers to view activity data</p>
            </div>
            <Switch defaultChecked disabled />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="text-base">Audit Logs</Label>
              <p className="text-sm text-gray-600">Access history of all alert actions</p>
            </div>
            <Button variant="outline" size="sm">
              View Logs
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex gap-2">
        <Button onClick={handleSave} className="bg-blue-600 hover:bg-blue-700">
          Save Settings
        </Button>
        <Button variant="outline">Reset to Defaults</Button>
      </div>
    </div>
  );
}
