package hu.bme.aut.android.bluetoothpositioning

data class Coordinate(val x: Float, val y: Float)

fun parseCoordinates(data: String): Pair<Coordinate, List<Coordinate>>? {
    // Format is the following:
    // estimated_coordinates;;anchor_1_coord;anchor_2_coord;anchor_3_coord etc.
    // Using a regex as validation:
    val regexPattern = """\d+(?:\.\d+)?,\d+(?:\.\d+)?;(;\d+(?:\.\d+)?,\d+(?:\.\d+)?)*""".toRegex()

    return if(regexPattern.matches(data)){
        val sections = data.split(";;")
        val estimatedCoord = sections[0].split(",").let { Coordinate(it[0].toFloat(), it[1].toFloat()) }

        val anchorCoords = sections[1].split(";").map {
            it.split(",").let { coord -> Coordinate(coord[0].toFloat(), coord[1].toFloat()) }
        }

        Pair(estimatedCoord, anchorCoords)
    }
    else {
        null
    }

}