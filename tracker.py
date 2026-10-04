print("================================")
print("       EXAMREADY TRACKER")
print("================================")

subjects = {
    "Physics": ["Electruc Charges and Fields", "Electrostatic Potential and Capacitance", "Cutrejt Electricity", "Moving Charges and Magnetism", "Magnetism and Matter", "Electromagnetic Induction","Alternating Current", "Electromagnetic Waves","Ray Optics", "Wave Optics", "Dual Nature of Radiation and Matter","Atoms", "Nuclei","Semiconductor Electronics"],
    "Chemistry": ["Solutions", "Electrochemistry", "Chemical Kinetics", "D and F Block Elements", "Coordination Compounds", "Haloalkanes and Haloarenes", "Alcohol, Phenol and Ethers", "Aldhehyde, Ketones and Carboxylic acids", "Amines", "Biomolecules"],
    "Maths": ["Relations and Functions", "Inverse Trigonometric Functions", "Matrices", "Determinants", "Continuity and Differentiability", "Application of Derivatives", "Integrals", "Differential Equations", "Vectors", "3D Geometry", "LPP","Probabilty"]
}

for subject in subjects:
    print("\n", subject)
    print("----------------------------")

    for chapter in subjects[subject]:
        print("[ ]", chapter)

print("\nStudy consistently and keep improving! 📚")
