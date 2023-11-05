package hu.bme.aut.android.bluetoothpositioning

import android.annotation.SuppressLint
import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp

@SuppressLint("UnusedMaterial3ScaffoldPaddingParameter")
@Composable
fun MapScreen(data: String) {

    if(parseCoordinates(data) == null){
        Toast.makeText(LocalContext.current, "Valid data could not be fetched.", Toast.LENGTH_LONG).show()
        return
    }
    val (estimated, anchors) = parseCoordinates(data)!!


    if(anchors.size <= 1){
        Toast.makeText(LocalContext.current, "There are too few anchors!", Toast.LENGTH_LONG).show()
        return
    }

    val maxX = anchors.maxByOrNull { it.x }!!.x
    val minX = anchors.minByOrNull { it.x }!!.x
    val maxY = anchors.maxByOrNull { it.y }!!.y
    val minY = anchors.minByOrNull { it.y }!!.y

    val widthRange = maxX - minX
    val heightRange = maxY - minY

    val screenWidthPx = LocalConfiguration.current.screenWidthDp
    val screenHeightPx = LocalConfiguration.current.screenHeightDp

    val widthAdjustment = 30
    val heightAdjustment = 30
    val adjustedWidth = screenWidthPx - widthAdjustment
    val adjustedHeight = screenHeightPx - heightAdjustment

    Box(
        modifier = Modifier
            .background(Color.LightGray)
            .fillMaxSize(),
        contentAlignment = Alignment.BottomStart
    ) {
        anchors.forEach { anchor ->
            Box(
                modifier = Modifier
                    .offset(
                        x = (((anchor.x - minX) / widthRange * adjustedWidth) + widthAdjustment/2).dp,
                        y = ((-((anchor.y - minY) / heightRange * adjustedHeight)) - heightAdjustment/2).dp
                    )
                    .size(10.dp)
                    .background(Color.Blue)
            )
        }

        estimated.forEach { estimate ->
            Box(
                modifier = Modifier
                    .offset(
                        x = (((estimate.x - minX) / widthRange * adjustedWidth) + widthAdjustment/2).dp,
                        y = ((-((estimate.y - minY) / heightRange * adjustedHeight)) - heightAdjustment/2).dp
                    )
                    .size(10.dp)
                    .background(Color.Red)
            )
        }
    }
}

@Preview
@Composable
fun MapScreenPreviewMultipleEstimatedPos(){
    MapScreen("4.1,5.1;5,6.5;5.9,6.4;;8,9;1,5;6,3")
}

@Preview
@Composable
fun MapScreenPreviewSingleEstimatedPos(){
    MapScreen("4.1,5.1;;8,9;1,5;6,3")
}

@Preview
@Composable
fun MapScreenPreviewNegativeNumbers(){
    MapScreen("-4.1,5.1;;-8,9;1,5;6,3")
}