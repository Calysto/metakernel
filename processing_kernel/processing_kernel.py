from jupyter_kernel import MagicKernel
from IPython.display import HTML
import sys

class ProcessingKernel(MagicKernel):
    implementation = 'Processing'
    implementation_version = '1.0'
    language = 'java'
    language_version = '0.1'
    banner = "Processing kernel - evaluates Processing programs"
    canvas_id = 0
    keywords = ["@pjs", "Array", "ArrayList", "HALF_PI",
                    "HashMap", "Object", "PFont", "PGraphics", "PI", "PImage",
                    "PShape", "PVector", "PrintWriter", "QUARTER_PI", "String",
                    "TWO_PI", "XMLElement", "abs", "acos", "alpha", "ambient",
                    "ambientLight", "append", "applyMatrix", "arc", "arrayCopy",
                    "asin", "atan", "atan2", "background", "beginCamera",
                    "beginRaw", "beginRecord", "beginShape", "bezier",
                    "bezierDetail", "bezierPoint", "bezierTangent",
                    "bezierVertex", "binary", "blend", "blendColor", "blue",
                    "boolean", "boolean", "box", "break", "brightness", "byte",
                    "byte", "camera", "case", "ceil", "char", "char", "class",
                    "color", "color", "colorMode", "concat", "constrain",
                    "continue", "copy", "cos", "createFont", "createGraphics",
                    "createImage", "createInput", "createOutput", "createReader",
                    "createWriter", "cursor", "curve", "curveDetail",
                    "curvePoint", "curveTangent", "curveTightness", "curveVertex",
                    "day", "default", "degrees", "directionalLight", "dist",
                    "double", "draw", "ellipse", "ellipseMode", "else",
                    "emissive", "endCamera", "endRaw", "endRecord", "endShape",
                    "exit", "exp", "expand", "extends", "false", "fill", "filter",
                    "final", "float", "float", "floor", "focused", "font", "for",
                    "frameCount", "frameRate", "frameRate", "frustum", "get",
                    "globalKeyEvents", "green", "height", "hex", "hint", "hour",
                    "hue", "if", "image", "imageMode", "implements", "import",
                    "int", "int", "join", "key", "keyCode", "keyPressed",
                    "keyPressed", "keyReleased", "keyTyped", "lerp", "lerpColor",
                    "lightFalloff", "lightSpecular", "lights", "line", "link",
                    "loadBytes", "loadFont", "loadImage", "loadPixels",
                    "loadShape", "loadStrings", "log", "long", "loop", "mag",
                    "map", "match", "matchAll", "max", "millis", "min", "minute",
                    "modelX", "modelY", "modelZ", "month", "mouseButton",
                    "mouseClicked", "mouseDragged", "mouseMoved", "mouseOut",
                    "mouseOver", "mousePressed", "mousePressed", "mouseReleased",
                    "mouseX", "mouseY", "new", "nf", "nfc", "nfp", "nfs",
                    "noCursor", "noFill", "noLights", "noLoop", "noSmooth",
                    "noStroke", "noTint", "noise", "noiseDetail", "noiseSeed",
                    "norm", "normal", "null", "online", "open", "ortho", "param",
                    "pauseOnBlur", "perspective", "pixels[]", "pmouseX",
                    "pmouseY", "point", "pointLight", "popMatrix", "popStyle",
                    "pow", "preload", "print", "printCamera", "printMatrix",
                    "printProjection", "println", "private", "public",
                    "pushMatrix", "quad", "radians", "random", "randomSeed",
                    "rect", "rectMode", "red", "requestImage", "resetMatrix",
                    "return", "reverse", "rotate", "rotateX", "rotateY",
                    "rotateZ", "round", "saturation", "save", "saveBytes",
                    "saveFrame", "saveStream", "saveStrings", "scale", "screen",
                    "screenX", "screenY", "screenZ", "second", "selectFolder",
                    "selectInput", "selectOutput", "set", "setup", "shape",
                    "shapeMode", "shininess", "shorten", "sin", "size", "smooth",
                    "sort", "specular", "sphere", "sphereDetail", "splice",
                    "split", "splitTokens", "spotLight", "sq", "sqrt", "static",
                    "status", "str", "stroke", "strokeCap", "strokeJoin",
                    "strokeWeight", "subset", "super", "switch", "tan", "text",
                    "textAlign", "textAscent", "textDescent", "textFont",
                    "textLeading", "textMode", "textSize", "textWidth", "texture",
                    "textureMode", "this", "tint", "translate", "triangle",
                    "trim", "true", "unbinary", "unhex", "updatePixels", "vertex",
                    "void", "while", "width", "year"]

    def get_usage(self):
        return "This is the Processing kernel based on Processingjs.org."

    def do_execute_direct(self, code):
        self.canvas_id += 1
        """%%processing - run contents of cell as a Processing script"""

        env = {"code": repr(code)[1:] if sys.version.startswith('2') else repr(code),
               "id": self.canvas_id}
        code = """
<canvas id="canvas_%(id)s"></canvas>
<script>
require(["http://cs.brynmawr.edu/gxk2013/examples/tools/alphaChannels/processing.js"], function () {
    var processingCode = %(code)s;
    var cc = Processing.compile(processingCode);
    var processingInstance = new Processing("canvas_%(id)s", cc);
});
</script>
""" % env
        html = HTML(code)
        self.Display(html)

    def get_completions(self, token):
        return [command for command in self.keywords if command.startswith(token)]

    def get_kernel_help_on(self, expr, level=0):
        if expr in self.keywords:
            return "See http://processingjs.org/reference/%s_/" % expr
        else:
            return "Sorry, no available help for '%s'"


if __name__ == '__main__': 
    from IPython.kernel.zmq.kernelapp import IPKernelApp 
    IPKernelApp.launch_instance(kernel_class=ProcessingKernel) 
