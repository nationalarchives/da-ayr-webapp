echo "List existing Service Task ..."
TASK=$(aws ecs list-tasks --cluster $ECS_CLUSTER --output text)

if [  -z "${TASK}"  ]
   then
   echo "First deployment - nothing to terminate - spin up new task"
else
   echo $TASK
   TASK=$(echo $TASK | tr 'TASKARNS' ' ')
   echo $TASK
   echo "Terminating existing task to recycle $TASK ..."
   aws ecs stop-task --cluster $ECS_CLUSTER --task $TASK
fi

echo "Run new task and check if running ..."
PENDING_TASK=""
while [  -z "${PENDING_TASK}"  ]
do 
   PENDING_TASK=$(aws ecs list-tasks --cluster $ECS_CLUSTER --desired-status RUNNING --output text)
   sleep 0.2
   echo "Restarting Service ..."
done

NEW_TASK=$(aws ecs list-tasks --cluster $ECS_CLUSTER --output text)


echo "New Cluster is up and running: $NEW_TASK"