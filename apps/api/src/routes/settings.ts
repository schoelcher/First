import { Router } from "express";
import { z } from "zod";
import { prisma } from "../lib/prisma";

const router = Router();

const schema = z.object({
  homeBase: z.string().min(5),
  settingsJson: z.string()
});

router.put("/:userId", async (req, res) => {
  const body = schema.parse(req.body);
  const user = await prisma.user.update({ where: { id: req.params.userId }, data: body });
  res.json(user);
});

router.delete("/:userId", async (req, res) => {
  await prisma.user.delete({ where: { id: req.params.userId } });
  res.status(204).send();
});

export default router;
