package hu.bme.aut.android.bluetoothpositioning

import android.content.ContentValues
import android.content.ContentValues.TAG
import android.graphics.Bitmap
import android.util.Log
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.navigation.NavHostController
import androidx.navigation.compose.rememberNavController
import kotlin.math.min


@Composable
fun OverlayMapScreen(
    image: Bitmap,
    topRightCoordinate: Coordinate,
    bottomLeftCoordinate: Coordinate,
    anchorOverlayCoordinates: List<Coordinate>,
    estimatedOverlayCoordinates: List<Coordinate>
) {
    Log.d(TAG, "Rendering started at " + System.currentTimeMillis().toString())
    val coordinateMarkerSize = 25f

    //Offset top right, bottom left and overlay coordinates to positive numbers,
    //so that the image with overlaid coordinates can be displayed properly
    var widthCoordinateOffset = 0f
    var heightCoordinateOffset = 0f
    for(coordinate in anchorOverlayCoordinates){
        widthCoordinateOffset = min(widthCoordinateOffset, coordinate.x)
        heightCoordinateOffset = min(heightCoordinateOffset, coordinate.y)
    }
    for(coordinate in estimatedOverlayCoordinates){
        widthCoordinateOffset = min(widthCoordinateOffset, coordinate.x)
        heightCoordinateOffset = min(heightCoordinateOffset, coordinate.y)
    }
    widthCoordinateOffset = min(widthCoordinateOffset, topRightCoordinate.x)
    heightCoordinateOffset = min(heightCoordinateOffset, topRightCoordinate.y)
    widthCoordinateOffset = min(widthCoordinateOffset, bottomLeftCoordinate.x)
    heightCoordinateOffset = min(heightCoordinateOffset, bottomLeftCoordinate.y)

    val anchorOffsetCoordinates = anchorOverlayCoordinates.map { coordinate ->
        Coordinate(coordinate.x - widthCoordinateOffset, coordinate.y - heightCoordinateOffset)
    }
    val estimatedOffsetCoordinates = estimatedOverlayCoordinates.map { coordinate ->
        Coordinate(coordinate.x - widthCoordinateOffset, coordinate.y - heightCoordinateOffset)
    }
    topRightCoordinate.x -= widthCoordinateOffset
    topRightCoordinate.y -= heightCoordinateOffset
    bottomLeftCoordinate.x -= widthCoordinateOffset
    bottomLeftCoordinate.y -= heightCoordinateOffset


    val screenWidthInPixels = LocalConfiguration.current.screenWidthDp * LocalConfiguration.current.densityDpi / 160f
    val screenHeightInPixels = LocalConfiguration.current.screenHeightDp * LocalConfiguration.current.densityDpi / 160f

    val imageWidth = image.width.toFloat()
    val imageHeight = image.height.toFloat()

    val scale = min(screenWidthInPixels / imageWidth, screenHeightInPixels / imageHeight)

    val scaledImageWidth = imageWidth * scale
    val scaledImageHeight = imageHeight * scale

    val widthOffset = (screenWidthInPixels - scaledImageWidth) / 2
    val heightOffset = (screenHeightInPixels - scaledImageHeight) / 2

    val imageWidthInCoordinate = topRightCoordinate.x - bottomLeftCoordinate.x
    val imageHeightInCoordinate = topRightCoordinate.y - bottomLeftCoordinate.y

    Log.d(TAG, "Screen resolution: $screenWidthInPixels x $screenHeightInPixels, " +
            "image resolution: $imageWidth x $imageHeight, " +
            "scale: $scale, " +
            "scaledImageWidth: $scaledImageWidth, scaledImageHeight: $scaledImageHeight, " +
            "widthOffset: $widthOffset, heightOffset: $heightOffset, " +
            "imageWidthInCoordinate: $imageWidthInCoordinate, imageHeightInCoordinate: $imageHeightInCoordinate")

    Box(modifier = Modifier.fillMaxSize()){
        Image(
            modifier = Modifier.fillMaxSize(),
            bitmap = image.asImageBitmap(),
            contentDescription = null,
            contentScale = ContentScale.Fit,
        )
        Canvas(modifier = Modifier.fillMaxSize()) {
            for (coordinate in anchorOffsetCoordinates) {
                val x = ((coordinate.x / imageWidthInCoordinate) * scaledImageWidth + widthOffset)
                val y = screenHeightInPixels - ((coordinate.y / imageHeightInCoordinate) * scaledImageHeight + heightOffset)
                if((x > scaledImageWidth + widthOffset || x < widthOffset) || (y > scaledImageHeight + heightOffset || y < heightOffset)){
                    Log.e(TAG, "Anchor coordinate is outside of the image: ${x}, ${y}\n" +
                            "Width offset: $widthOffset, height offset: $heightOffset\n" +
                            "Scaled image width: $scaledImageWidth, scaled image height: $scaledImageHeight")
                    continue
                }
                Log.d(TAG,"Rendering anchor coordinate: ${coordinate.x}, ${coordinate.y}, " + "x: $x, y: $y")
                drawRect(
                    color = Color.Blue,
                    topLeft = Offset(x-coordinateMarkerSize/2, y-coordinateMarkerSize/2),
                    size = Size(coordinateMarkerSize, coordinateMarkerSize)
                )
            }

            for (coordinate in estimatedOffsetCoordinates) {
                val x = ((coordinate.x / imageWidthInCoordinate) * scaledImageWidth + widthOffset)
                val y = screenHeightInPixels - ((coordinate.y / imageHeightInCoordinate) * scaledImageHeight + heightOffset)
                if((x > scaledImageWidth + widthOffset || x < widthOffset) || (y > scaledImageHeight + heightOffset || y < heightOffset)){
                    Log.e(TAG, "Coordinate is outside of the image: ${x}, ${y}\n" +
                            "Width offset: $widthOffset, height offset: $heightOffset\n" +
                            "Scaled image width: $scaledImageWidth, scaled image height: $scaledImageHeight")
                    continue
                }
                Log.d(TAG,"Rendering estimated coordinate: ${coordinate.x}, ${coordinate.y}, " + "x: $x, y: $y")
                drawRect(
                    color = Color.Red,
                    topLeft = Offset(x-coordinateMarkerSize/2, y-coordinateMarkerSize/2),
                    size = Size(coordinateMarkerSize, coordinateMarkerSize)
                )
            }
            Log.d(TAG, "Rendering ended at " + System.currentTimeMillis().toString())
        }
    }
}

@Preview
@Composable
fun MapOverlayPreview(){
    val context = LocalContext.current
    val image: Bitmap = loadImageFromInternalStorage(context)!!
    val topRightCoordinate = Coordinate(5.0f, 5.0f)
    val bottomLeftCoordinate = Coordinate(-5.0f, -5.0f)
    val anchorOverlayCoordinates = listOf(
        Coordinate(5.0f, 5.0f),
        Coordinate(-5.0f, -5.0f),
        Coordinate(-5.0f, -2.5f),
        Coordinate(-5.0f, 0.0f),
    )
    val estimatedOverlayCoordinates = listOf(
        Coordinate(5.0f, -5.0f),
        Coordinate(-5.0f, 5.0f),
        Coordinate(0.5f, 0.0f),
        Coordinate(2.5f, 5.5f),
        Coordinate(1f, 3f)
    )
    OverlayMapScreen(image, topRightCoordinate, bottomLeftCoordinate, anchorOverlayCoordinates, estimatedOverlayCoordinates)
}
