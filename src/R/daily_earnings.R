#! /usr/local/bin/RScript
library(readr)
library(data.table)
library(ggplot2)
library(ggthemes)

# Set working directories
setwd("~/bu/Desktop/uber_driver_strategy/")
figures.dir = "~/bu/Desktop/uber_driver_strategy/plots/"

# Read data
dd = data.table(read.delim("./plots_data/daily_earnings_all_zones.csv.gz",
                           sep=","))
dd[, strategy := as.character(strategy)]
dd[, strategy := factor(strategy, levels=c("naive", "reloc", "flexi", "reloc_flexi"))]
levels(dd$strategy) = c("naive", "relocation", "flexible", "flexible-relocation")

dd[, day := as.character(day)]
dd[, day := factor(day, levels=c("Sunday", "Monday", "Tuesday", "Wednesday", 
                                 "Thursday", "Friday", "Saturday"))]

# Daily earnings plot
mycols = c("orange", "red", "darkgreen", "blue")
p1 = ggplot(data=dd, aes(x=factor(day), y=earnings, fill=strategy))
p1 = p1 + stat_summary(fun.y="mean")
p1 = p1 + geom_bar(stat='identity', position = "dodge")
p1 = p1 + scale_fill_manual(name="", values=mycols)
p1 = p1 + scale_y_continuous(name="Earnings ($ / workday)", expand=c(0,0), limits=c(0,400))
p1 = p1 + theme_bw()
p1 = p1 + theme(legend.position = c(0.25, 0.85),
                legend.direction = "horizontal",
                axis.title.x = element_blank(),
                axis.text.x = element_text(size=5),
                axis.text.y = element_text(size=5),
                axis.title.y = element_text(size=7),
                legend.margin = margin(t=0, r=0, b=0, l=0, unit = "pt"),
                legend.key.size = unit(0.32, "cm"),
                legend.text = element_text(size = 5, face="italic"))
p1
ggsave(paste0(figures.dir, "daily_earnings_avg.pdf"), w=16, h=4, units ="cm")
