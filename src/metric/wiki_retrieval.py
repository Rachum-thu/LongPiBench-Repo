from .base import NLGMetric
from bert_score import score
from typing import List


class WikiQAMetric(NLGMetric):
    
    def _evaluate_pair(self, llm_response: str, labels: List[str]) -> float:
        """get the recall rate, check if the llm_response contains any of the labels"""
        recall_total = len(labels)
        recall_count = 0
        
        llm_response = llm_response.lower()
        labels = [label.lower() for label in labels]
        for label in labels:
            if label in llm_response:
                recall_count += 1
        return recall_count / recall_total

if __name__ == "__main__":
    # Test the WikiQAMetric with provided cases
    llm_responses = [
        "Problems like dry skin, rashes, and yellow discoloration can sometimes be signs of underlying health conditions, including liver disease, kidney issues, or autoimmune ailments. Regularly examining your skin and noticing changes in its texture, color, or unusual spots can help in immediate diagnosis and treatment.",
        "The primary sources of water pollution in urban areas include air pollution settling into water bodies through atmospheric deposition, runoff from construction sites, leaching of chemicals and toxins from landfills into the groundwater, use of fertilizers and pesticides in urban agricultural activities, and untreated sewage from residential areas.",
        "Some common indoor air pollutants that can affect respiratory health include:\n\n1. A deadly, colorless, and odorless gas that can emanate from faulty heating equipment or poorly ventilated appliances. Breathing it can cause headache, dizziness, vomiting, and even death in high concentrations. \n\n2. Radon, a radioactive gas that can seep into homes from the ground. Radon is the second leading cause of lung cancer in the U.S.\n\n3. Secondhand smoke from tobacco which contains over 7,000 chemicals, many of which are toxic and can cause cancer.\n\n4. Pet dander, which are tiny, even microscopic, flecks of skin shed by animals with fur or feathers. Proteins found in pet dander can cause allergic reactions and trigger asthma symptoms.\n\n5. Pesticides that are commonly used in homes for pest control. Residues can remain in the air and on surfaces and cause a variety of health effects, including disruption of the immune system and developmental problems in children.\n\n6. Volatile Organic Compounds (VOCs) which can be emitted by cleaning supplies, air fresheners, and some types of furniture and carpet. They can cause eye, nose, and throat irritation to damage to the liver, kidney, and central nervous system.\n\n7. Asbestos, often found in older insulation materials. When disturbed, its fibers can be inhaled and cause lung disease.\n\n8. Dampness that can facilitate the growth of mold spores, inducing allergic reactions and asthma attacks.\n\n9. Formaldehyde, a chemical released from various sources in homes, can cause eye, nose, and throat irritation and increase risk of asthma and allergic reactions.",
    ]

    labels = [
        ["Skin Health"],
        ["Air Pollution", "Construction Sites", "Leaching", "Agricultural Run-off", "Sewage"],
        ["Carbon Monoxide", "Radon", "Tobacco Smoke", "Pet Dander", "Dust Mites", "Pesticides", "Volatile Organic Compounds (VOCs)", "Asbestos", "Mold and Mildew", "Formaldehyde"],
    ]

    metric = WikiQAMetric()
    # results = metric.evaluate(llm_responses, labels)
    # print(results)  # Expected output: List of lists with F1 Scores for each label
    # [0.8150850534439087, 0.8558191061019897, 0.8114909529685974]

    results = metric.evaluate(llm_responses, labels, em_instead=True)
    print(results)  # Expected output: List of lists with EM Scores for each label
    # [0.0, 0.8, 0.6]
    