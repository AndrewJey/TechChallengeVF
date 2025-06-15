# -*- coding: utf-8 -*-
# Refrencias e Importes
from apscheduler.schedulers.blocking import BlockingScheduler # Importar un scheduler bloqueador 
from TechChallengeVF.TechChallengeVF import scrape
# Scheduler para ejecutar el scraping cada hora
scheduler = BlockingScheduler()
scheduler.add_job(scrape, 'interval', hours=1)
# Iniciar el scheduler
if __name__ == "__main__":
    scheduler.start()
    print("Scheduler iniciado, ejecutando scraping cada hora...")