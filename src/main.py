"""Execute main, test logic.  To be replaced."""

import logging


# each module/file should provide a global-level logger using this statement
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the main function and logic."""
    setup_logging()
    logger.info('main starting: %s', 'asdf')
    logger.warning('sample warn')
    s = "eric writes silly variable names"
    test_string = "Hello"
    logger.info('%s - %s', s, test_string)


def test_func_with_type(arg: str) -> bool:
    """Return an arbitrary comparison."""
    return arg == "nothing"


def setup_logging() -> None:
    """Set up logging."""
    # TODO:
    # add file rotation
    # make json logging so we can easily ingest elsewhere
    logging.basicConfig(
        filename='gloomhaven-monster-ai.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(threadName)s  - %(message)s')


if __name__ == '__main__':
    """Run the main function as a script."""
    main()
