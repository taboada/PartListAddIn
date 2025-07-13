from collections import defaultdict

# Liste des matériaux basée sur materials.json
ORIENTED_MATERIALS = {"pine", "walnut", "triply", "oak", "chen", "pin", "merisier", "contreplaque"}
NON_ORIENTED_MATERIALS = {"medium", "mdf", "agglomeré", "ParticleBoard"}

def get_part_list(root_comp):
    part_list = defaultdict(lambda: {'quantity': 0, 'names': set()})  # Utiliser un set pour les noms uniques
    processed_components = set()  # Stocker les noms uniques pour éviter les doublons

    # Parcourir les occurrences pour identifier les composants uniques
    occurrences = root_comp.occurrences
    for occurrence in occurrences:
        sub_comp = occurrence.component
        # Utiliser un tuple (nom du composant, nom du parent) comme clé unique
        comp_key = (sub_comp.name, sub_comp.parentComponent.name if sub_comp.parentComponent else 'root')
        if comp_key in processed_components or occurrence.isReferencedDocument:
            continue  # Ignorer les composants externes ou déjà traités
        
        # Utiliser la boîte englobante du composant pour dimensions brutes
        bounding_box = sub_comp.boundingBox
        if not bounding_box:
            continue
        
        min_point = bounding_box.minPoint
        max_point = bounding_box.maxPoint
        
        dims = [
            (max_point.x - min_point.x) * 10,  # Conversion en mm
            (max_point.y - min_point.y) * 10,
            (max_point.z - min_point.z) * 10
        ]
        dims = [round(dim) for dim in dims]  # Arrondi à l'entier
        dims.sort(reverse=True)
        length, width, thickness = dims
        
        # Déterminer le matériau à partir du premier corps valide
        material = 'Non défini'
        for body in sub_comp.bRepBodies:
            if body.isValid and body.material:
                material = body.material.name
                break
        
        # Déterminer l'orientation
        if any(mat in material.lower() for mat in ORIENTED_MATERIALS):
            orientation = 'longueur'
        elif any(mat in material.lower() for mat in NON_ORIENTED_MATERIALS):
            orientation = 'non applicable'
        else:
            orientation = 'non défini'
        
        part_key = (length, width, thickness, material, orientation)
        # Ajouter les noms de toutes les occurrences du même composant
        for occ in occurrences:
            if occ.component == sub_comp:
                occ_name = occ.name if occ.name else sub_comp.name
                part_list[part_key]['names'].add(occ_name)
        part_list[part_key]['quantity'] = len(part_list[part_key]['names'])  # Mettre à jour la quantité
        
        processed_components.add(comp_key)
    
    # Vérifier aussi les corps au niveau racine (si applicable, comme fallback)
    for body in root_comp.bRepBodies:
        if not body.isValid:
            continue
        
        material = body.material.name if body.material else 'Non défini'
        bounding_box = body.boundingBox
        min_point = bounding_box.minPoint
        max_point = bounding_box.maxPoint
        
        dims = [
            (max_point.x - min_point.x) * 10,
            (max_point.y - min_point.y) * 10,
            (max_point.z - min_point.z) * 10
        ]
        dims = [round(dim) for dim in dims]
        dims.sort(reverse=True)
        length, width, thickness = dims
        
        if any(mat in material.lower() for mat in ORIENTED_MATERIALS):
            orientation = 'longueur'
        elif any(mat in material.lower() for mat in NON_ORIENTED_MATERIALS):
            orientation = 'non applicable'
        else:
            orientation = 'non défini'
        
        part_key = (length, width, thickness, material, orientation)
        body_name = body.name if body.name else f"Body_{len(part_list[part_key]['names']) + 1}"
        part_list[part_key]['quantity'] += 1
        part_list[part_key]['names'].add(body_name)
    
    return part_list

def format_part_list(part_list):
    output = 'Fiche de débit des pièces capables :\n\n'
    output += f'{"Qté":<5} {"Longueur (mm)":<15} {"Largeur (mm)":<15} {"Épaisseur (mm)":<15} {"Matériau":<20} {"Noms":<30}\n'
    output += '-' * 100 + '\n'
    
    for (length, width, thickness, material, orientation), data in part_list.items():
        names_str = ', '.join(sorted(data['names']))[:27] + '...' if len(', '.join(data['names'])) > 27 else ', '.join(sorted(data['names']))
        output += f'{data["quantity"]:<5} {length:<15} {width:<15} {thickness:<15} {material:<20} {names_str:<30}\n'
    
    return output