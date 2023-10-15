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
import java.security.AccessController.getContext

@SuppressLint("UnusedMaterial3ScaffoldPaddingParameter")
@Composable
fun MapScreen(data: String) {

    if(parseCoordinates(data) == null){
        Toast.makeText(LocalContext.current, "Valid data could not be fetched.", Toast.LENGTH_LONG).show()
        return
    }
    val (estimated, anchors) = parseCoordinates(data)!!


    if(anchors.isEmpty())
        return

    val maxX = maxOf(estimated.x, anchors.maxOf { it.x })
    val minX = minOf(estimated.x, anchors.minOf { it.x })
    val maxY = maxOf(estimated.y, anchors.maxOf { it.y })
    val minY = minOf(estimated.y, anchors.minOf { it.y })

    val widthRange = maxX - minX
    val heightRange = maxY - minY

    val screenWidthPx = LocalConfiguration.current.screenWidthDp
    val screenHeightPx = LocalConfiguration.current.screenHeightDp

    val adjustedWidth = screenWidthPx - 10
    val adjustedHeight = screenHeightPx - 10

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
                        x = ((anchor.x - minX) / widthRange * adjustedWidth).dp,
                        y = (-((anchor.y - minY) / heightRange * adjustedHeight)).dp
                    )
                    .size(10.dp)
                    .background(Color.Blue)
            )
        }

        Box(
            modifier = Modifier
                .offset(
                    x = ((estimated.x - minX) / widthRange * adjustedWidth).dp,
                    y = (-((estimated.y - minY) / heightRange * adjustedHeight)).dp
                )
                .size(10.dp)
                .background(Color.Red)
        )
    }
}

@Preview
@Composable
fun MapScreenPreview(){
    MapScreen("4,5;;8,9;1,5;6,3")
}