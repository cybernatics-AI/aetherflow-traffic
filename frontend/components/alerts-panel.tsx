"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Bell, AlertTriangle, Info, CheckCircle, X } from 'lucide-react'

interface Alert {
  id: string
  type: "critical" | "warning" | "info"
  title: string
  message: string
  timestamp: string
  location?: string
}

export function AlertsPanel() {
  const alerts: Alert[] = [
    {
      id: "1",
      type: "critical",
      title: "High Congestion Detected",
      message: "Traffic backup detected at Main & 5th intersection",
      timestamp: "2 min ago",
      location: "Intersection 14"
    },
    {
      id: "2",
      type: "warning",
      title: "Sensor Maintenance Required",
      message: "Traffic sensor showing degraded performance",
      timestamp: "15 min ago",
      location: "Broadway & Oak"
    },
    {
      id: "3",
      type: "info",
      title: "Optimization Complete",
      message: "AI optimization cycle completed successfully",
      timestamp: "1 hour ago"
    }
  ]

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "critical":
        return <AlertTriangle className="w-4 h-4 text-red-400" />
      case "warning":
        return <Bell className="w-4 h-4 text-yellow-400" />
      default:
        return <Info className="w-4 h-4 text-blue-400" />
    }
  }

  const getAlertBadge = (type: string) => {
    switch (type) {
      case "critical":
        return "bg-red-500/20 text-red-400 border-red-500/30"
      case "warning":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
      default:
        return "bg-blue-500/20 text-blue-400 border-blue-500/30"
    }
  }

  return (
    <Card className="bg-slate-900/50 border-slate-800/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-amber-400" />
          <span className="text-slate-100">System Alerts</span>
          <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 ml-auto">
            {alerts.length}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50 hover:border-slate-600/50 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                {getAlertIcon(alert.type)}
                <span className="text-sm font-medium text-slate-200">{alert.title}</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge className={`${getAlertBadge(alert.type)} text-xs px-2 py-0.5`}>
                  {alert.type}
                </Badge>
                <Button variant="ghost" size="sm" className="w-6 h-6 p-0 hover:bg-slate-700">
                  <X className="w-3 h-3" />
                </Button>
              </div>
            </div>
            <p className="text-xs text-slate-400 mb-2">{alert.message}</p>
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>{alert.timestamp}</span>
              {alert.location && <span>{alert.location}</span>}
            </div>
          </div>
        ))}
        
        <Button variant="outline" className="w-full mt-4 border-slate-600 text-slate-300 hover:bg-slate-800">
          <CheckCircle className="w-4 h-4 mr-2" />
          Mark All as Read
        </Button>
      </CardContent>
    </Card>
  )
}
