#! /usr/local/bin/RScript
library(readr)
library(data.table)
library(ggplot2)
library(ggthemes)
library(ggmap)
library(geojsonio)
library(rgdal)
library(sp)
library(maps)
library(maptools)

# Set working directories
setwd("~/bu/Desktop/uber_driver_strategy/")
figures.dir = "~/bu/Desktop/uber_driver_strategy/plots/"

# Read the geojson file
city_zones = geojson_read("./data/taxi_zones/taxi_zones.geojson", what="sp")
city_zones = fortify(city_zones, region='taxi_zone')
city_zones_df = data.table(city_zones)

# Read demands data
earnings_df = data.table(read.delim("./plots_data/earning_heatmap.csv.gz", sep=","))

# Merge dataframes
dd = merge(city_zones_df, earnings_df, by.x='id', by.y='zone', all.x=TRUE, allow.cartesian=TRUE)
dd[, earnings := as.numeric(earnings)]
dd[, time := as.factor(time)]
dd[, strategy := as.factor(strategy)]
levels(dd$time) = c("Morning 8AM", "Noon 12PM", "Evening 5PM", "Night 10PM")
levels(dd$strategy) = c("naive", "relocation")
# Box plot
mycols = c("orange", "red")
p = ggplot(data=dd[strategy=="naive" | strategy=="relocation"], aes(x=strategy, y=earnings, fill=strategy))
p = p + geom_boxplot(outlier.size=0.5, outlier.alpha=0.3)
p = p + scale_x_discrete(name="")
p = p + scale_y_continuous(name="Earnings ($ / workday)", expand=c(0,0))
p = p + scale_fill_manual(guide=FALSE, values=mycols)
p = p + theme_bw()
p = p + theme(legend.position = c(0.28,0.9),
              legend.direction = "horizontal",
              legend.title = element_blank(),
              legend.text = element_text(size = 5),
              axis.text.x = element_text(size = 5, face="italic"),
              axis.text.y = element_text(size = 5),
              axis.title.y = element_text(size = 7),
              axis.title.x = element_blank(),
              legend.margin = margin(t=0, r=0, b=0, l=0, unit = "pt"),
              legend.key.size = unit(0.2, "cm"))
p
ggsave(paste0(figures.dir, "earnings_heatmap.pdf"), w=6, h=4, units="cm")


# Plot on map
# mycol = c("seagreen","yellow", "yellow2","red", "red4")
# p0 = ggmap(get_map(c(lon=-74.0, lat=40.74), scale="auto", zoom=10, maptype="roadmap", color="bw"), 
#           extent="device")
# p = p0 + facet_grid(strategy ~ time, switch="y")
# p = p + geom_polygon(aes(long, lat, group = group, fill=earnings),
#                      data=dd,
#                      alpha=0.8,
#                      size=0.2,
#                      colour="black")
# p = p + scale_fill_gradientn(name="$ / workday", colours=mycol)
# p = p + scale_x_continuous(name="", expand = c(0,0), limits=c(-74.3, -73.7))
# p = p + scale_y_continuous(name="", expand = c(0,0), limits=c(40.48, 40.91))
# p = p + theme_few()
# p = p + theme(strip.background = element_blank(),
#               axis.line = element_blank(),
#               axis.title = element_blank(),
#               axis.ticks = element_blank(),
#               axis.text = element_blank(),
#               strip.text.x = element_text(margin = margin(t=0.03,0,0.2,0, "cm"), size = 6),
#               strip.text.y = element_text(size = 7),
#               legend.position = c(0.04,0.89),
#               legend.margin = margin(t=0, r=0, b=0, l=0, unit = "pt"),
#               legend.key.size = unit(0.2, "cm"),
#               legend.title = element_text(size = 7),
#               legend.text = element_text(size = 6),
#               plot.margin = unit(c(0,0.2,0,0), 'cm'))
# p
# ggsave(paste0(figures.dir, "earnings_heatmap.pdf"), w=16, h=8, units="cm")
