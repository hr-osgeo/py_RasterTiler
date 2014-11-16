#-------------------------------------------------------------------------------
# Name:        cropToSegments
# Purpose:
#
# Author:      darko.boto
# Drscription: Crop GDAL raster to arbitrary number of tiles
# Created:     14.11.2014
# Copyright:   (c) darko.boto 2014
# Licence:     MIT
#-------------------------------------------------------------------------------
try:
  from osgeo import gdal, gdalconst,ogr, osr
except:
  import gdal, ogr, osr

import os, sys, subprocess
import math

def main():
    inFile = 'data/croatia.mbtiles'
    inDS = gdal.Open(inFile)
    if inDS is None:
        print 'Could not open' + inFile
        sys.exit(1)

    # -- Get raster info
    geoTransform = inDS.GetGeoTransform()
    minX = geoTransform[0]
    maxY = geoTransform[3]
    maxX = minX + geoTransform[1] * inDS.RasterXSize
    minY = maxY + geoTransform[5] * inDS.RasterYSize

    width_px = inDS.RasterXSize
    height_px = inDS.RasterYSize

    print '**************************'
    print '***  INPUT RASTER INFO ***'
    print 'INPUT RASTER SIZE: ', width_px, ' X ', height_px
    print 'NUMBER OF INPUT RASTER BANDS:', inDS.RasterCount
    print 'INPUT RASTER EXTENT: ', minX, minY, maxX, maxY
    print '**************************'
    #inPproj = inDS.GetProjection()

    segments = 4
    # Uncoment if you want run script in interactive mod
    #segments = getNumberOfSegments(height_px, width_px)

    print '*** OUTPUT RASTER INFO ***'
    print 'NUMBER OF TILES: ',int(segments) * int(segments)
    print 'OUTPUT TILE SIZE ', height_px / int(segments), ' X ', width_px / int(segments)
    print '**************************'
    print '*** START EXECUTE GDAL ***'


    # -- Calculate grid
    minXminY = [minX, minY]
    maxXmaxY = [maxX, maxY]

    x = maxXmaxY[0] - minXminY[0]
    y = maxXmaxY[1] - minXminY[1]

    xsize = x / int(segments)
    ysize = y / int(segments)

    for xi in range(int(segments)):
        for yi in range(int(segments)):
            segment_extent = [(xi * xsize) + minXminY[0] , (yi * ysize) + minXminY[1], ((xi * xsize) + xsize) + minXminY[0] , ((yi * ysize) + ysize) + minXminY[1]]

            # -- Crop image

            # Create gdalwarp command
            # ofStr = ' -of ' + outGDALFormat + ' '
            # resStr = ' -tr %s %s '%(pixSizeX, pixSizeY)
            # projectionStr = ''' -t_srs '%s' ''' %(projection)
            bbStr = ' -te %s %s %s %s '%(segment_extent[0],segment_extent[1],segment_extent[2],segment_extent[3])
            overwriteStr = ' -overwrite '
            warpOptions = bbStr + overwriteStr
            out_filename = 'out_' + str(xi + 1) + str(yi + 1) + '.tif'
            gdalwarpCMD = 'gdalwarp' + warpOptions + ' ' + inFile + ' ' + out_filename

            print '---- Column:', xi + 1, 'Row:', yi + 1
            print 'Segment extent', segment_extent
            print 'Execute: ',gdalwarpCMD
            print 'Output file name: out_' + str(xi + 1) + str(yi + 1) + '.tif'
            os.system(gdalwarpCMD)

    print '*** CROP TO SEGMENTS EXECUTE SUCCSESFULY*** '

def getNumberOfSegments(height_px,width_px):
    while True:
        segments = raw_input( "Please set number of sections x and y axis" )
        if segments.isdigit() == False:
            continue
            segments = raw_input( "Type a number!" )

        print '*** OUTPUT RASTER INFO ***'
        print 'NUMBER OF TILES: ',int(segments) * int(segments)
        print 'OUTPUT TILE SIZE ', height_px / int(segments), ' X ', width_px / int(segments)
        print '**************************'

        execute = raw_input( "Do you want to proceed? Y/N" )
        if str(execute) == 'Y' or str(execute) == 'y':
            return segments
        else:
            print 'Exit script!'
            break

if __name__ == '__main__':
    main()
