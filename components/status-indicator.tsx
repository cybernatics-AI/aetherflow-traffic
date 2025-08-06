import { Badge } from "@/components/ui/badge"
import { Activity, AlertTriangle, XCircle } from "lucide-react"

interface StatusIndicatorProps {
  status: "active" | "maintenance" | "offline"
}

export function StatusIndicator({ status }: StatusIndicatorProps) {
  const getStatusConfig = () => {
    switch (status) {
      case "active":
        return {
          icon: Activity,
          label: "System Active",
          variant: "default" as const,
          className: "bg-green-500/20 text-green-400 border-green-500/30",
        }
      case "maintenance":
        return {
          icon: AlertTriangle,
          label: "Maintenance",
          variant: "secondary" as const,
          className: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
        }
      case "offline":
        return {
          icon: XCircle,
          label: "Offline",
          variant: "destructive" as const,
          className: "bg-red-500/20 text-red-400 border-red-500/30",
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <Badge className={config.className}>
      <Icon className="w-3 h-3 mr-1" />
      {config.label}
    </Badge>
  )
}
