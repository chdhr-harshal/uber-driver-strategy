#! /usr/local/bin/RScript

library(data.table)
library(ggplot2)
library(ggthemes)
library(ggmap)
library(geojsonio)
library(rgdal)
library(sp)
library(maps)
library(maptools)
library(forcats)
library(dplyr)
library(tidyr)

# Set working directories
setwd("~/bu/Desktop/uber_driver_strategy/")
figures.dir = "~/bu/Desktop/uber_driver_strategy/plots/"

# Read data
simulation_earnings_csv <- read_csv("./plots_data/simulation_earnings_Monday.csv.gz")
dd = data.table(simulation_earnings_csv)
dd[, strategy := factor(strategy, levels=c("naive","reloc","flexi","reloc_flexi"))]
levels(dd$strategy) = c("naive", "relocation", "flexible", "flexible-relocation")

dd[, surge := factor(surge, levels=c("No", "Passive", "Active"))]
levels(dd$surge) = c("No surge", "Surge", "Surge Chasing")

# Plot strategies and earnings
p = ggplot(dd[home_zone=="2A"], aes(x=strategy, y=earnings, fill=surge))
p = p + geom_boxplot(outlier.size=0.5, outlier.alpha=0.3)
p = p + scale_x_discrete(name="")
p = p + scale_y_continuous(name="Earnings ($ / workday)")
p = p + scale_fill_manual(name="", values=c('#ffffbf','#99d594','#fc8d59'))
# p = p + scale_fill_brewer(palette="Set1", type="div", direction=-1)
p = p + theme_bw()
p = p + theme(legend.position = c(0.27,0.9),
            legend.title = element_blank(),
            legend.text = element_text(size = 5),
            legend.margin = margin(t=0, r=0, b=0, l=0, unit = "pt"),
            legend.key.size = unit(0.3, "cm"),
            legend.direction = "horizontal",
            axis.text.x = element_text(size = 5, face="italic"),
            axis.text.y = element_text(size = 5),
            axis.title.y = element_text(size = 7),
            axis.title.x = element_blank())
p
ggsave(paste0(figures.dir, "simulated_earnings.pdf"), w=8.5, h=4, units="cm")

# Read data
simulation_actions_csv <- read_csv("~/bu/Desktop/uber_driver_strategy/plots_data/simulation_actions_Monday.csv.gz")
dd = data.table(simulation_actions_csv)

dd[, surge := factor(surge, levels=c("No", "Passive", "Active"))]
dd[, strategy := factor(strategy, levels=c("naive","reloc","flexi","reloc_flexi"))]
levels(dd$strategy) = c("Naive", "Relocation", "Flexible", "Flexible Relocation")

dd1 = dd[strategy == 'Naive']
dd2 = dd[strategy == 'Relocation' & action == 'a2' & surge == "Passive"]
dd3 = dd[strategy == 'Flexible' & action == 'a1' & surge == "No" & start_zone == end_zone]
dd4 = dd[strategy == 'Flexible Relocation' & action == 'a2' & surge == "Passive"]
dd5 = dd[strategy == 'Flexible Relocation' & action == 'a1' & surge == "No" & start_zone == end_zone]

# Popular desitionation for relocations
dd2 = group_by(dd2, end_zone) %>% summarize(n=n())
dd2 = data.table(dd2)
dd2[, strategy := "relocation"]
dd4 = group_by(dd4, end_zone) %>% summarize(n=n())
dd4 = data.table(dd4)
dd4[, strategy := "flexible-relocation"]
dd8 = rbind(dd2, dd4)
dd8[, end_zone := as.factor(end_zone)]

dd8$end_zone = fct_collapse(dd8$end_zone, 
                           "West Side" = c("2B","3A","3B", "3C", "6A", "7A"),
                           "Midtown South" = c("2A"),
                           "East Side" = c("2C", "5A", "5B", "5C", "6B", "7B"),
                           "Queens" = c("8","12","13","14","9"),
                           "Brooklyn" = c("10","11","15"),
                           "Midtown" = c("4A","4B","4C"),
                           "Financial District" = c("1"),
                           "Harlem" = c("7C"),
                           "Bronx" = c("16"),
                           "Newark" = c("18"),
                           "Staten Island" = c("17"))

dd8[, end_zone := factor(end_zone, levels=c("West Side", "Midtown", "East Side",
                                   "Midtown South", "Financial District", "Queens","Brooklyn", "Harlem", 
                                   "Bronx", "Newark", "Staten Island"))]
dd8[, strategy := factor(strategy, levels=c("relocation","flexible-relocation"))]


mycols = c("red", "blue")
p = ggplot(data=dd8[end_zone == "West Side" | end_zone == "Midtown" | end_zone == "East Side" | end_zone == "Queens" | end_zone == "Midtown South"
                    | end_zone == "Financial District" | end_zone == "Brooklyn"],
           aes(end_zone, n, fill=strategy))
p = p + geom_bar(stat="identity", position="dodge")
p = p + scale_fill_manual(name="", values=mycols)
p = p + scale_y_continuous(name="# relocations")
p = p + theme_bw()
p = p + theme(legend.position = c(0.2, 0.89),
              legend.direction = "horizontal",
              axis.title.x = element_blank(),
              axis.text.x = element_text(size=5),
              axis.text.y = element_text(size=5),
              axis.title.y = element_text(size=7),
              legend.margin = margin(t=0, r=0, b=0, l=0, unit = "pt"),
              legend.key.size = unit(0.2, "cm"),
              legend.text = element_text(size = 5, face="italic"))
p
ggsave(paste0(figures.dir, "relocation_endzones.pdf"), w=16, h=4, units="cm")

# Percentage of active drivers
dd6 = group_by(dd3, N, i) %>% summarize(n=n()) %>% group_by(N) %>% summarize(n=n())
dd7 = group_by(dd5, N, i ) %>% summarize(n=n()) %>% group_by(N) %>% summarize(n=n())
dd6 = data.table(dd6)
dd6[, strategy := "flexi"]
dd7 = data.table(dd7)
dd7[, strategy := "reloc_flexi"]

cols <- c("flexible"="darkgreen","flexible-relocation"="blue")
p = ggplot(data=dd6, aes(x=N/6, y=1-n/1000.0))
p = p + geom_line(aes(colour="flexible"), size=0.5, linetype=4)
p = p + geom_line(data=dd7, aes(x=N/6, y=1 -n/1000, colour="flexible-relocation"), size=0.5)
p = p + scale_color_manual(name="", values=cols)
p = p + scale_linetype_manual(name="", values=c("Flexi_lty"=4, "Flexi_reloc_lty"=1))
p = p + theme_bw()
p = p + scale_x_continuous(name="", expand = c(0,0),
                          breaks=c(seq(1,24,3)),
                          labels=c("1AM", "4AM", "7AM", "10AM", "1PM", "4PM", "7PM", "10PM"))
p = p + scale_y_continuous(name="% Active Drivers",
                           breaks=c(seq(0,1.1,0.25)))
p = p + theme(legend.position = c(0.23,0.85),
              legend.direction = "horizontal",
              legend.text = element_text(size = 5, face="italic"),
              axis.text.x = element_text(size = 5),
              axis.text.y = element_text(size = 5),
              axis.title.y = element_text(size = 7),
              legend.margin = margin(t=0, r=0, b=0, l=0, unit = "pt"),
              legend.key.size = unit(0.2, "cm"))
p
ggsave(paste0(figures.dir, "simulated_schedules.pdf"), w=8.5, h=3.7, units="cm")


dd9 = group_by(dd3, i, N) %>% summarize(n=n()) %>% group_by(i)
dd9 = data.table(dd9)
dd10 = do.call(rbind,by(dd9,cumsum(c(0,diff(dd9$N)!=1)),
                 function(g) data.frame(imin=min(g$N),imax=max(g$N),irange=diff(range(g$N)))))
dd10$strategy = "flexible"

dd11 = group_by(dd5, i, N) %>% summarize(n=n()) %>% group_by(i)
dd11 = data.table(dd11)
dd12 = do.call(rbind,by(dd11,cumsum(c(0,diff(dd11$N)!=1)), function(g) data.frame(imin=min(g$N),imax=max(g$N),irange=diff(range(g$N)))))
dd12$strategy = "flexible-relocation"

dd13 = rbind(dd10,dd12)
dd13 = data.table(dd13)


p = ggplot(data=dd13, aes(x=irange, color=strategy)) + geom_density()
p