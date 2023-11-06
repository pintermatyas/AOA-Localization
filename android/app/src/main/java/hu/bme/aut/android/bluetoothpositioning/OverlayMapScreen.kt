package hu.bme.aut.android.bluetoothpositioning

import android.content.ContentValues
import android.graphics.Bitmap
import android.util.Log
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import kotlin.math.min


@Composable
fun MapWithOverlay(
    image: Bitmap,
    topRightCoordinate: Coordinate,
    bottomLeftCoordinate: Coordinate,
    overlayCoordinates: List<Coordinate>
) {

    //Offset top right, bottom left and overlay coordinates to positive numbers,
    //so that the image with overlaid coordinates can be displayed properly
    var widthCoordinateOffset = 0f
    var heightCoordinateOffset = 0f
    for(coordinate in overlayCoordinates){
        widthCoordinateOffset = min(widthCoordinateOffset, coordinate.x)
        heightCoordinateOffset = min(heightCoordinateOffset, coordinate.y)
    }
    widthCoordinateOffset = min(widthCoordinateOffset, topRightCoordinate.x)
    heightCoordinateOffset = min(heightCoordinateOffset, topRightCoordinate.y)
    widthCoordinateOffset = min(widthCoordinateOffset, bottomLeftCoordinate.x)
    heightCoordinateOffset = min(heightCoordinateOffset, bottomLeftCoordinate.y)

    val offsetCoordinates = overlayCoordinates.map { coordinate ->
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

    Log.e(
        ContentValues.TAG, "Screen resolution: $screenWidthInPixels x $screenHeightInPixels, " +
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
            for (coordinate in offsetCoordinates) {
                val x = ((coordinate.x / imageWidthInCoordinate) * scaledImageWidth + widthOffset)
                val y = ((coordinate.y / imageHeightInCoordinate) * scaledImageHeight + heightOffset)
                Log.e(
                    ContentValues.TAG,
                    "Coordinate: ${coordinate.x}, ${coordinate.y}, " +
                            "x: $x, y: $y")
                drawCircle(color = Color.Red, radius = 5f, center = Offset(x, y))
            }
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
    val overlayCoordinates = listOf(
        Coordinate(5.0f, 5.0f),
        Coordinate(-5.0f, -5.0f),
        Coordinate(0.0f, 0.0f),
        Coordinate(2.5f, 2.5f),
    )
    MapWithOverlay(image, topRightCoordinate, bottomLeftCoordinate, overlayCoordinates)
}
