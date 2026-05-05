class PointLight:
    def __init__(self, pos, color, intensity, radius,  coneHalfAngle=30.0, directionAngle=90.0, volumetricintensity=0.2, z=0.5):
        self.pos = pos
        self.color = color
        self.intensity = intensity
        self.radius = radius
        self.coneHalfAngle = coneHalfAngle
        self.directionAngle = directionAngle
        self.volumetricIntensity = volumetricintensity
        self.zValue = z
