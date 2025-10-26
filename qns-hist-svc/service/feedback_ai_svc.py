from pydantic_ai import Agent, ModelHTTPError, PromptedOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from models.db_models import AttemptFeedback, QuestionAttempt
from models.models import EvaluationOutput
from utils.logger import log
from utils.utils import get_envvar

log.info(f"Evaluation Model set: {get_envvar('EVALUATION_MODEL_NAME')}")

EVALUATION_SYSTEM_PROMPT = "You are an senior software engineer at a big software company. You are evaluating the quality of answers provided by potential candidates. You will be given a question which contains: The title, description, code template, solution sample, difficulty level, category and the submitted solution. You will evaluate the submitted solution and provide feedback on the candidates performance and provide pointers for the candidate to improve."

data_extraction_agent = Agent(
    OpenAIChatModel(
        get_envvar("EVALUATION_MODEL_NAME"),
        provider=OpenAIProvider(
            base_url=get_envvar("OPENAI_COMPAT_API_ENDPOINT"),
            api_key=get_envvar("OPENAI_COMPAT_API_KEY"),
        ),
    ),
    system_prompt=EVALUATION_SYSTEM_PROMPT,
    output_type=PromptedOutput(EvaluationOutput),
)


async def evalation_question_attempt(qa_id: int) -> None:
    log.info(f"Evaluating question attempt: {qa_id}")

    if not await QuestionAttempt.filter(id=qa_id).exists():
        log.warning(f"Question attempt not found: {qa_id}")
        return

    qa = await QuestionAttempt.get(id=qa_id)

    prompt = f"Given the following question given to the candidate: \n Title: {qa.title} \n Difficulty: {qa.difficulty} \n Category: {qa.category} \n Description: {qa.description} \n Code Template: ```{qa.code_template}``` \n Solution Sample: ```{qa.solution_sample}``` \n You are to evaluate and provide a comprehensive feedback on the following submitted solution: \n ```{qa.submitted_solution}```"

    try:
        result = await data_extraction_agent.run(prompt)

        log.debug(result.output)

        await AttemptFeedback.create(
            question_attempt_id=qa_id,
            feedback=result.output.feedback,
        )
    except ModelHTTPError as e:
        log.warning(f"Failed to evaluate question attempt: {qa_id}")
        log.debug(e)
