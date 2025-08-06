import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Home, Trophy, TrendingUp, BarChart3, Settings, Users, Globe, Shield } from 'lucide-react'

export function Navigation() {
  const navigationItems = [
    {
      href: "/home",
      icon: Home,
      title: "Mobile Dashboard",
      description: "Driver-focused mobile interface"
    },
    {
      href: "/rewards",
      icon: Trophy,
      title: "Rewards Center",
      description: "AETHER tokens and leaderboards"
    },
    {
      href: "/trading",
      icon: TrendingUp,
      title: "Trading Platform",
      description: "NFT marketplace and derivatives"
    },
    {
      href: "/analytics",
      icon: BarChart3,
      title: "Advanced Analytics",
      description: "Deep insights and reporting"
    }
  ]

  const adminTools = [
    {
      href: "/settings",
      icon: Settings,
      title: "System Configuration",
      description: "Platform settings and controls"
    },
    {
      href: "/users",
      icon: Users,
      title: "User Management",
      description: "Driver accounts and permissions"
    },
    {
      href: "/network",
      icon: Globe,
      title: "Network Topology",
      description: "Infrastructure management"
    },
    {
      href: "/security",
      icon: Shield,
      title: "Security Center",
      description: "Access control and monitoring"
    }
  ]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* User Navigation */}
      <Card className="bg-slate-900/50 border-slate-800/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-slate-100">Platform Navigation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {navigationItems.map((item) => (
              <Link key={item.href} href={item.href}>
                <Button
                  variant="outline"
                  className="w-full h-24 flex-col gap-2 border-orange-600/50 text-orange-400 hover:bg-orange-600 hover:text-white bg-slate-800/50 backdrop-blur-sm transition-all duration-300 hover:shadow-lg hover:shadow-orange-500/25"
                >
                  <item.icon className="w-6 h-6" />
                  <div className="text-center">
                    <div className="text-sm font-semibold">{item.title}</div>
                    <div className="text-xs opacity-75">{item.description}</div>
                  </div>
                </Button>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Admin Tools */}
      <Card className="bg-slate-900/50 border-slate-800/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-slate-100">Administrative Tools</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {adminTools.map((item) => (
              <Link key={item.href} href={item.href}>
                <Button
                  variant="outline"
                  className="w-full h-24 flex-col gap-2 border-slate-600/50 text-slate-300 hover:bg-slate-700 hover:text-white bg-slate-800/50 backdrop-blur-sm transition-all duration-300"
                >
                  <item.icon className="w-6 h-6" />
                  <div className="text-center">
                    <div className="text-sm font-semibold">{item.title}</div>
                    <div className="text-xs opacity-75">{item.description}</div>
                  </div>
                </Button>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
