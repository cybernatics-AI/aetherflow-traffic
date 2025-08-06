"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { MapPin, Activity, Clock, Zap } from 'lucide-react'

export function TrafficMetrics() {
  const metrics = [
    { label: "Network Efficiency", value: 87, color: "emerald", unit: "%" },
    { label: "Response Time", value: 75, color: "blue", unit: "ms" },
    { label: "Throughput", value: 92, color: "orange", unit: "%" },
    { label: "Reliability", value: 99, color: "purple", unit: "%" }
  ]

  const intersectionData = [
    { id: "INT-14", name: "Main & 5th", efficiency: 92, status: "optimal", vehicles: 847 },
    { id: "INT-15", name: "Broadway & Oak", efficiency: 68, status: "congested", vehicles: 1203 },
    { id: "INT-16", name: "Central & Pine", efficiency: 85, status: "active", vehicles: 692 },
  ]

  return (
    <Card className="bg-slate-900/50 border-slate-800/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-slate-100">
          <div className="w-8 h-8 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-lg flex items-center justify-center">
            <MapPin className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="text-lg font-semibold">Live Traffic Metrics</div>
            <div className="text-sm text-slate-400 font-normal">Real-time performance indicators</div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Performance Metrics */}
        <div className="space-y-4">
          {metrics.map((metric, index) => (
            <div key={index} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400 font-medium">{metric.label}</span>
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-semibold ${
                    metric.color === 'emerald' ? 'text-emerald-400' :
                    metric.color === 'blue' ? 'text-blue-400' :
                    metric.color === 'orange' ? 'text-orange-400' :
                    'text-purple-400'
                  }`}>
                    {metric.value}{metric.unit}
                  </span>
                  <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                </div>
              </div>
              <Progress value={metric.value} className="h-2" />
            </div>
          ))}
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-700/50">
          <div className="text-center p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Activity className="w-4 h-4 text-orange-400" />
              <div className="text-lg font-bold text-orange-400">14</div>
            </div>
            <div className="text-xs text-slate-400">Active Signals</div>
          </div>
          <div className="text-center p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Zap className="w-4 h-4 text-blue-400" />
              <div className="text-lg font-bold text-blue-400">2.1k</div>
            </div>
            <div className="text-xs text-slate-400">Vehicles/hr</div>
          </div>
        </div>

        {/* Intersection Status */}
        <div className="space-y-3 pt-4 border-t border-slate-700/50">
          <h4 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-400" />
            Intersection Status
          </h4>
          {intersectionData.map((intersection) => (
            <div key={intersection.id} className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <div className="text-sm font-medium text-slate-200">{intersection.id}</div>
                  <div className="text-xs text-slate-400">{intersection.name}</div>
                </div>
                <Badge className={
                  intersection.status === "optimal" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" :
                  intersection.status === "congested" ? "bg-red-500/20 text-red-400 border-red-500/30" :
                  "bg-blue-500/20 text-blue-400 border-blue-500/30"
                }>
                  {intersection.status}
                </Badge>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Efficiency</span>
                  <span className="text-slate-200 font-mono">{intersection.efficiency}%</span>
                </div>
                <Progress value={intersection.efficiency} className="h-1.5" />
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Flow Rate</span>
                  <span className="text-slate-200 font-mono">{intersection.vehicles} veh/hr</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
