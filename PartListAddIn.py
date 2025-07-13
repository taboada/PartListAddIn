import adsk.core, adsk.fusion, traceback
import os
import sys

# Ajouter le chemin du sous-dossier PartListCommand au sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'PartListCommand'))

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        if not app.activeDocument:
            ui.messageBox('Aucun document ouvert. Veuillez ouvrir un document avant d\'exécuter cet add-in.')
            return
        
        product = app.activeProduct
        if not product:
            ui.messageBox('Aucun produit actif. Veuillez ouvrir un modèle dans l\'environnement Design.')
            return
        
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('Cet add-in nécessite l\'environnement Design.')
            return

        root_comp = design.rootComponent
        if not root_comp:
            ui.messageBox('Aucun composant racine trouvé.')
            return

        from PartListCommand import get_part_list, format_part_list
        part_list = get_part_list(root_comp)
        output = format_part_list(part_list)
        ui.messageBox(output, 'Liste des pièces capables')

    except:
        if ui:
            ui.messageBox('Erreur : ' + traceback.format_exc())

def stop(context):
    pass