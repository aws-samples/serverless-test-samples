#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import aws_cdk as cdk

from infrastructure.config import InfrastructureConfig
from infrastructure.test_harness.test_infrastructure_stack import TestInfrastructureStack

app = cdk.App()
config = InfrastructureConfig.from_cdk_context(app.node)
TestInfrastructureStack(app, config.test_harness_stack_name(), env=cdk.Environment(region=config.region))
app.synth()
