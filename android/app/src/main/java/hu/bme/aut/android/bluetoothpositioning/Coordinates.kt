package hu.bme.aut.android.bluetoothpositioning

import android.content.Context
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.IOException
import java.io.ObjectInputStream
import java.io.ObjectOutputStream

data class Coordinate(var x: Float, var y: Float)

fun parseCoordinates(data: String): Pair<List<Coordinate>, List<Coordinate>>? {
    /*
    Format is the following:
    estimated_1_coordinates;estimated_2_coordinates;;anchor_1_coord;anchor_2_coord;anchor_3_coord etc.
    Using a regex as validation:
    TODO: Add anchor and tag IDs to the format
    */
    val regexPattern = """(-?\d+(\.\d+)?,-?\d+(\.\d+);)+(;-?\d+(\.\d+)?,-?\d+(\.\d+)?)+""".toRegex()


    return if(regexPattern.matches(data)){
        val sections = data.split(";;")
        val estimatedCoords = sections[0].split(";").map {
            it.split(",").let { estimatedCoord -> Coordinate(estimatedCoord[0].toFloat(), estimatedCoord[1].toFloat())  }
        }

        val anchorCoords = sections[1].split(";").map {
            it.split(",").let { anchorCoord -> Coordinate(anchorCoord[0].toFloat(), anchorCoord[1].toFloat()) }
        }

        Pair(estimatedCoords, anchorCoords)
    }
    else {
        null
    }

}

data class SavableCoordinateData(
    val coordinates: List<Coordinate>,
    val ids: List<Int>
)