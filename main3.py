from browser_use import Agent, Browser, ChatBrowserUse
from browser_use.browser.views import BrowserStateSummary  
from browser_use.agent.views import AgentOutput  
import asyncio

# Callback síncrono  
def my_step_callback(  
    browser_state: BrowserStateSummary,  
    agent_output: AgentOutput,  
    step_number: int  
):  
    print(f"-----------------------------")
    print(f"Paso {step_number} completado")  
    print(f"URL actual: {browser_state.url}")  
    print(f"Próximo objetivo: {agent_output.current_state.next_goal}")  
    print(f"-----------------------------")


async def example():
    browser = Browser(
         use_cloud=False  # Uncomment to use a stealth browser on Browser Use Cloud


    )

    llm = ChatBrowserUse()

    agent = Agent(
        task="Busca las ultimas series de TV en https://www.pogdesign.co.uk/cat/recent-additions y dime las 5 series que pueden tener más exito. Cruza datos con visualizaciones de Youtube, reseñas en webs especializadas y puntacion en IMDB y escribe en un .md por cada show escribiendo un articulo extenso y en español de review del show serie destacando la popularidad en los sitios webs consultados y contando el argumento, tambien añade en que plataforma está disponible y cuando es la fecha de estreno, genera el .md estructurado y listo para publicar en un blog.",
        llm=llm,
        browser=browser,
        register_new_step_callback= my_step_callback
        
    )
    
    history = await agent.run()
 
    return history


    



if __name__ == "__main__":
    history = asyncio.run(example())