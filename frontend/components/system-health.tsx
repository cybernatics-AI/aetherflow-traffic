"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Activity, Wifi, Database, Cpu } from 'lucide-react'

interface SystemHealthProps {
  latency: number
  systemLoad: number
  status: "active" | "maintenance" | "offline"
}

export function SystemHealth({ latency, systemLoad, status }: SystemHealthProps) {
  const getLatencyColor = () => {
    if (latency < 20) return "text-emerald-400"
    if (latency < 50) return "text-yellow-400"
    return "text-red-400"
  }

  const getLoadColor = () => {
    if (systemLoad < 60) return "text-emerald-400"
    if (systemLoad < 80) return "text-yellow-400"
    return "text-red-400"
  }

  return (
    <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
      <CardContent className="p-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Wifi className={`w-4 h-4 ${getLatencyColor()}`} />
            <div className="text-right">
              <div className={`text-sm font-mono ${getLatencyColor()}`}>{latency}ms</div>
              <div className="text-xs text-slate-400">Latency</div>
            </div>
          </div>
          
          <div className="w-px h-8 bg-slate-700"></div>
          
          <div className="flex items-center gap-2">
            <Cpu className={`w-4 h-4 ${getLoadColor()}`} />
            <div className="text-right">
              <div className={`text-sm font-mono ${getLoadColor()}`}>{systemLoad}%</div>
              <div className="text-xs text-slate-400">Load</div>
            </div>
          </div>
          
          <div className="w-px h-8 bg-slate-700"></div>
          
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-400" />
            <div className="text-right">
              <div className="text-sm font-mono text-blue-400">99.9%</div>
              <div className="text-xs text-slate-400">Uptime</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
