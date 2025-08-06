"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, Minus, type LucideIcon } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: number
  unit: string
  change: number
  icon: LucideIcon
  description: string
  color: "teal" | "emerald" | "blue" | "purple" | "orange"
  trend: "up" | "down" | "stable"
}

const colorClasses = {
  teal: {
    gradient: "from-teal-900/50 to-cyan-800/30",
    border: "border-teal-700/50 hover:border-teal-600/50",
    icon: "from-teal-500 to-cyan-500",
    text: "text-teal-200",
    accent: "text-teal-300"
  },
  emerald: {
    gradient: "from-emerald-900/50 to-green-800/30",
    border: "border-emerald-700/50 hover:border-emerald-600/50",
    icon: "from-emerald-500 to-green-500",
    text: "text-emerald-200",
    accent: "text-emerald-300"
  },
  blue: {
    gradient: "from-blue-900/50 to-cyan-800/30",
    border: "border-blue-700/50 hover:border-blue-600/50",
    icon: "from-blue-500 to-cyan-500",
    text: "text-blue-200",
    accent: "text-blue-300"
  },
  purple: {
    gradient: "from-purple-900/50 to-violet-800/30",
    border: "border-purple-700/50 hover:border-purple-600/50",
    icon: "from-purple-500 to-violet-500",
    text: "text-purple-200",
    accent: "text-purple-300"
  },
  orange: {
    gradient: "from-orange-900/50 to-amber-800/30",
    border: "border-orange-700/50 hover:border-orange-600/50",
    icon: "from-orange-500 to-amber-500",
    text: "text-orange-200",
    accent: "text-orange-300"
  }
}

export function MetricCard({ 
  title, 
  value, 
  unit, 
  change, 
  icon: Icon, 
  description, 
  color, 
  trend 
}: MetricCardProps) {
  const classes = colorClasses[color]
  
  const getTrendIcon = () => {
    switch (trend) {
      case "up":
        return <TrendingUp className="w-3 h-3" />
      case "down":
        return <TrendingDown className="w-3 h-3" />
      default:
        return <Minus className="w-3 h-3" />
    }
  }

  const getTrendColor = () => {
    switch (trend) {
      case "up":
        return "text-emerald-400 bg-emerald-500/20 border-emerald-500/30"
      case "down":
        return "text-red-400 bg-red-500/20 border-red-500/30"
      default:
        return "text-slate-400 bg-slate-500/20 border-slate-500/30"
    }
  }

  return (
    <Card className={`bg-gradient-to-br ${classes.gradient} ${classes.border} transition-all duration-300 hover:shadow-lg backdrop-blur-sm`}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className={`w-12 h-12 bg-gradient-to-r ${classes.icon} rounded-xl flex items-center justify-center shadow-lg`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          <Badge className={`${getTrendColor()} flex items-center gap-1 px-2 py-1`}>
            {getTrendIcon()}
            <span className="text-xs font-medium">
              {change > 0 ? '+' : ''}{change.toFixed(1)}%
            </span>
          </Badge>
        </div>

        <div className="space-y-2">
          <h3 className={`text-sm font-medium ${classes.text}`}>{title}</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </span>
            <span className={`text-sm ${classes.accent}`}>{unit}</span>
          </div>
          <p className={`text-xs ${classes.accent}`}>{description}</p>
        </div>

        {/* Progress indicator for percentage values */}
        {unit.includes('%') && (
          <div className="mt-4">
            <Progress value={Math.min(100, Math.max(0, value))} className="h-2" />
          </div>
        )}

        {/* Trend indicator */}
        <div className="flex items-center gap-2 mt-4 pt-3 border-t border-slate-700/50">
          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
          <span className="text-xs text-slate-400">Live data • Updated 2s ago</span>
        </div>
      </CardContent>
    </Card>
  )
}
