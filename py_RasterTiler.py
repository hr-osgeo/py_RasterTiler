#-------------------------------------------------------------------------------
# Name:        cropToSegments
# Purpose:
#
# Author:      Darko Boto darko.boto@gmail.com
# Drscription: Crop GDAL raster to arbitrary number of tiles
# Created:     14.11.2014
# Copyright:   (c) darko.boto 2014
# Licence:     MIT
#-------------------------------------------------------------------------------
try:
  from osgeo import gdal, ogr, osr
except:
  import gdal, ogr, osr

import os, sys, subprocess

import math

def main():
    # TODO -  cmd arguments
    inFile = 'data/croatia.mbtiles'
    epsg = 3765

    inDS = gdal.Open(inFile)
    if inDS is None:
        print 'Could not open' + inFile
        sys.exit(1)

    # -- Get input raster info
    # -- Get extent
    geoTransform = inDS.GetGeoTransform()
    minX = geoTransform[0]
    maxY = geoTransform[3]
    maxX = minX + geoTransform[1] * inDS.RasterXSize
    minY = maxY + geoTransform[5] * inDS.RasterYSize
    # -- Get size
    width_px = inDS.RasterXSize
    height_px = inDS.RasterYSize
    # -- Get input SRS
    SRS_wkt = inDS.GetProjection()
    SRS_in = osr.SpatialReference()
    SRS_in.ImportFromWkt(SRS_wkt)
    in_SRS = str(SRS_in.ExportToProj4())


    print '**************************'
    print '***  INPUT RASTER INFO ***'
    print 'INPUT RASTER SIZE: ', width_px, ' X ', height_px
    print 'NUMBER OF INPUT RASTER BANDS:', inDS.RasterCount
    print 'INPUT RASTER EXTENT: ', minX, minY, maxX, maxY
    print '**************************'
    #inPproj = inDS.GetProjection()

    # Default number of segments
    segments = 2
    # Uncoment if you want run script in interactive mod
    #segments = getNumberOfSegments(height_px, width_px)

    # -- Get output SRS
    SRS_out = osr.SpatialReference()
    SRS_out.ImportFromEPSG(epsg) # harcdcode SRS
    out_SRS = str(SRS_out.ExportToProj4())

    print '*** OUTPUT RASTER INFO ***'
    print 'NUMBER OF TILES: ', int(segments) * int(segments)
    print 'OUTPUT TILE SIZE ', height_px / int(segments), ' X ', width_px / int(segments)
    print 'OUTPUT EPSG:', epsg
    print '**************************'
    print '*** START EXECUTE GDAL ***'

    # Convert coordinate - reprojet gdalwarp need coordinate in target SRS
    coordTransform = osr.CoordinateTransformation(SRS_in, SRS_out)
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(minX, minY)
    point.Transform(coordTransform)
    print point.GetX(), point.GetY()

    # -- Calculate grid
    minXminY = ogr.Geometry(ogr.wkbPoint)
    minXminY.AddPoint(minX, minY)
    minXminY.Transform(coordTransform)
    maxXmaxY = ogr.Geometry(ogr.wkbPoint)
    maxXmaxY.AddPoint(maxX, maxY)
    maxXmaxY.Transform(coordTransform)

    x = maxXmaxY.GetX() - minXminY.GetX()
    y = maxXmaxY.GetY() - minXminY.GetY()

    xsize = x / int(segments)
    ysize = y / int(segments)

    for xi in range(int(segments)):
        for yi in range(int(segments)):
            segment_extent = [(xi * xsize) + minXminY.GetX() , (yi * ysize) + minXminY.GetY(), ((xi * xsize) + xsize) + minXminY.GetX() , ((yi * ysize) + ysize) + minXminY.GetY()]

            # -- Crop image

            # Create gdalwarp command
            # ofStr = ' -of ' + outGDALFormat + ' '
            # resStr = ' -tr %s %s '%(pixSizeX, pixSizeY)
            extentStr = ' -te %s %s %s %s '%(segment_extent[0],segment_extent[1],segment_extent[2],segment_extent[3])
            srsStr = '-s_srs "' + in_SRS + '"' + ' -t_srs "' + out_SRS + '"'
            overwriteStr = ' -overwrite '
            out_filename = 'out_' + str(xi + 1) + str(yi + 1) + '.tif'

            warpOptions = extentStr + srsStr + overwriteStr

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

        execute = raw_input( 'Number of tiles are ' + + 'Do you want to proceed? Y/N' )
        if str(execute) == 'Y' or str(execute) == 'y':
            return segments
        else:
            print 'Exit script!'
            #break
            sys.exit( 1 )

if __name__ == '__main__':
    main()
